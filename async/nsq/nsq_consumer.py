# Standard packages
import os
from uuid import uuid4

# Internal packages
from augury_data_sdk.modules import base_consumer, utils
from nsqworker import nsqworker
from nsqworker.helpers import register_nsq_topics, post_message_to_nsq
from augury_data_sdk.monitor.monitor import Monitor
import datetime

# External packages
import nsq
from raven import Client as RavenClient
import random

external_logger = utils.get_logger(name="Configuration Loader")


class NSQConsumer(base_consumer.BaseConsumer):
    def __init__(self, **kwargs):
        super(NSQConsumer, self).__init__(raven_client=RavenClient())
        self.logger.info("Initialising microservice-feature-store Consumer...")
        self.consumer_id = str(uuid4())
        self.nsq_publish_topic = kwargs.pop('nsq_publish_topic')
        self.consume_topic = kwargs.pop('consume_topic')
        if not self.consume_topic:
            raise Exception("Please define consume_topic")
        self.consume_channel = kwargs.pop('consume_channel')
        if not self.consume_channel:
            raise Exception("Please define consume_channel")
        self.nsqd_http_addresses = kwargs.pop('nsqd_http_addresses').split(",")

        register_nsq_topics(self.nsqd_http_addresses, [self.consume_topic])

        if 'lookupd_http_addresses' in kwargs:
            self.lookupd_http_addresses = kwargs.pop('lookupd_http_addresses').split(",")
        else:
            self.lookupd_http_addresses = []
        self.logger.info(f"nsqd_http_addresses : {self.nsqd_http_addresses}")
        self.expose_prometheus = kwargs.pop("expose_prometheus")
        self.monitor = Monitor(service_name="microservice-feature-store",
                               service_topic=self.consume_topic,
                               service_channel=self.consume_channel,
                               expose_prometheus=self.expose_prometheus)

        self.report_metric(metric_name="initialized", unique_identifier=self.consumer_id)

    def parse_message(self, message):
        message_ts = utils.parse_nsq_message_timestamp(message=message)
        self.logger.info(
            f"Now processing", tags={"message_id": message.id, "created_at": message_ts})
        decoded_body = utils.decode_message_bytes(message.body)
        return message.id, decoded_body

    def message_process_implementation(self, message_id, message_body):
        # Do work
        data = []
        self.logger.info(f"Done processing message", tags={"message_id": message_id})
        return data

    def run(self):
        def handle_exc(message, e):
            self.logger.error("Failed processing message", tags={"error": str(e)})
            self.monitor.report_message_process_failure()
            w.io_loop.add_callback(message.requeue)

        def process_message(message):
            self.report_metric(metric_name="message_consumed", unique_identifier=self.consumer_id)
            # Parse message
            start_proc_msg_time = datetime.datetime.now()
            message_id, message_body = self.parse_message(message)
            # Process payload
            messages_payload = self.message_process_implementation(message_id, message_body)
            # Output message
            for message_payload in messages_payload:
                if self.nsq_publish_topic:
                    serialized_detection = utils.get_nsq_payload(message_payload)
                    nsqd_http_address = random.choice(self.nsqd_http_addresses)
                    result = post_message_to_nsq(nsqd_http_address=nsqd_http_address,
                                                 topic=self.nsq_publish_topic,
                                                 message_payload=serialized_detection)
                    tags = {
                        "session_id": message_payload.machine_context.grouping_id,
                        "machine_id": message_payload.machine_context.machine_id,
                        "message_id": message_id
                    }
                    try:
                        if result.status_code != 200:
                            self.logger.error(f"Failed to post message to NSQ", tags=tags)
                    except AttributeError:
                        self.logger.critical(f"Invalid response object when posting to NSQ", tags=tags)
                    else:
                        self.logger.info(f"Published to NSQ", tags=tags)
                        self.report_metric(metric_name="message_produced", unique_identifier=self.consumer_id)

            message_proc_time = round((datetime.datetime.now() - start_proc_msg_time).total_seconds() * 1000)
            self.monitor.report_message_process_success(duration=message_proc_time)
            self.logger.info(f"[FINISH] done processing message", tags={"message_id": message_id,
                                                                        "timesMs": message_proc_time})

        # Initialize and run NSQ worker
        w = nsqworker.ThreadWorker(service_name="microservice-feature-store",
                                   message_handler=process_message,
                                   exception_handler=handle_exc,
                                   concurrency=1,
                                   topic=self.consume_topic,
                                   channel=self.consume_channel,
                                   lookupd_http_addresses=self.lookupd_http_addresses)
        w.subscribe_worker()
        nsq.run()


if __name__ == '__main__':
    external_logger.info("Load environment variables")
    configuration = dict()
    configuration['consume_topic'] = os.getenv("CONSUME_TOPIC")
    configuration['consume_channel'] = os.getenv("CONSUME_CHANNEL")
    configuration['nsq_publish_topic'] = os.getenv("NSQ_PUBLISH_TOPIC")
    external_logger.info("Discover NSQD host")
    configuration['lookupd_http_addresses'] = os.getenv('DATA_SERVICES_LOOKUPD_HTTP_ADDRESSES')
    configuration['nsqd_http_addresses'] = os.getenv('NSQD_DATA_SERVICES_HTTP_ADDRESSES')
    configuration['expose_prometheus'] = os.environ.get("EXPOSE_PROMETHEUS", None)
    consumer_instance = NSQConsumer(**configuration)
    consumer_instance.run()
    external_logger.info("Exiting.")
