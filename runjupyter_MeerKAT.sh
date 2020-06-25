echo "executing notebook: "
jupyter nbconvert --to notebook --execute $HOME/processMeerKAT_tutorial_clean.ipynb --output $HOME/processMeerKAT_tutorial_run.ipynb --ExecutePreprocessor.timeout=None --ExecutePreprocessor.kernel_name=casapy
