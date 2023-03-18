# add virtual environment if it doesn't already exist
if ! [[ -d env ]]; then
    echo Adding virtual environment 
    python3 -m venv env

    # create pip.conf if doesn't exist
    echo Creating env/pip.conf
    ( cat <<'EOF'
[install]
user = false
EOF
    ) > env/pip.conf
fi

# activate the virtual environment
source env/bin/activate
pip3 install -r requirements.txt
echo Installed requirements and virtual environment: ./run.sh to run