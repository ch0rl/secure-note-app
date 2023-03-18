# Convert .ui files to one .py file

echo "" > NoteAppUI.py
for f in ./*.ui;
do
    pyuic5 $f >> NoteAppUI.py
done
