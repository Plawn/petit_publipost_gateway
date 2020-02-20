rm -rf modules > /dev/null
mkdir modules
cd  modules
# git pull the excel_env
git clone "https://git.dev.juniorisep.com/phoenix/publiposting-services/excel-publiposting.git" || { echo "failed to clone" ; exit 2; }
cd excel-publiposting
yarn install || { echo "failed to install" ; exit 2; }
yarn build || { echo "failed to build" ; exit 2; }
cd ..
# we are inside the modules folder
# we can install other modules if needed
