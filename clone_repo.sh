LOWERCASE_DASH_NAME=microservice-$1
UPPERCASE_UNDERSCORE_NAME=MICROSERVICE_$1
UPPERCASE_UNDERSCORE_NAME=$(echo "$UPPERCASE_UNDERSCORE_NAME" | tr '[:lower:]' '[:upper:]')
UPPERCASE_UNDERSCORE_NAME=$(echo "$UPPERCASE_UNDERSCORE_NAME" | tr - _)

mkdir $LOWERCASE_DASH_NAME
cp -r microservice-genai-template/. $LOWERCASE_DASH_NAME
cd $LOWERCASE_DASH_NAME
mv deploy/microservice-genai-template deploy/$LOWERCASE_DASH_NAME
rm -rf .git
LC_ALL=C find . -type f -exec sed -i '' -e 's/microservice-genai-template/'$LOWERCASE_DASH_NAME'/g' {} \;
LC_ALL=C find . -type f -exec sed -i '' -e 's/MICROSERVICE_AUGURY_GEN_AI/'$UPPERCASE_UNDERSCORE_NAME'/g' {} \;
echo '# '$LOWERCASE_DASH_NAME > README.md
rm -rf .git README-CLONE-GUIDE.md

git init
git config --global credential.helper store
echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials
git add .
git commit -a -m 'Create new microservice'
git remote add origin git@github.com:augurysys/$LOWERCASE_DASH_NAME
git push -u origin master
