#!bash
module load python
module load icommands

cd iRODS_tests

#test datai
echo "Copying testdata: cp -r /home/christin/testdata $TMPDIR"
cp -r /home/christin/testdata $TMPDIR

for i in {1..5}; do
echo "python testIRODS.py -p -r pocCompound -s /home/christin/astron/lisa_poci_pocCompound_files${i}.csv"
python testIRODS.py -p -r pocCompound -s /home/christin/astron/lisa_poci_pocCompound_files${i}.csv
python testIRODS.py -c

echo "python testIRODS.py -p -r pocCompound -s /home/christin/astron/lisa_poci_pocCompound_files${i}.csv"
python testIRODS.py -p -r pocCompound2 -s /home/christin/astron/lisa_poci_pocCompound2_files${i}.csv
python testIRODS.py -c

echo "python testIRODS.py -p -r pocCompound -s /home/christin/astron/lisa_poci_pocCompound_files${i}.csv"
python testIRODS.py -p -d -r pocCompound -s /home/christin/astron/lisa_poci_pocCompound_coll${i}.csv
python testIRODS.py -c

echo "python testIRODS.py -p -r pocCompound -s /home/christin/astron/lisa_poci_pocCompound_files${i}.csv"
python testIRODS.py -p -d -r pocCompound2 -s /home/christin/astron/lisa_poci_pocCompound2_coll${i}.csv
python testIRODS.py -c
done
