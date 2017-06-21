import sys
import os
import gffutils
import argparse
import json

def add_matches(matches,array):
    for m in matches:
        trans = {}
        trans['mRNA'] = '.'.join(m.id.split('.',2)[:2]) #hack to recover mRNA from PFAM gff which doesn't include a query field
        trans['Contig'] = m.seqid
        trans['Source'] = m.source
        trans['Score'] = m.score
        trans['Prediction']=m["Name"]
        array.append(trans)
def main(argv, wayout):
        if not len(argv):
                argv.append("-h")
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
        parser.add_argument('-d','--database', help="gffutils sqlite database")
        parser.add_argument('-j','--json', help="report in json format")
        args = parser.parse_args(argv)
        gffutils.constants.always_return_list = False
        db = gffutils.interface.FeatureDB(args.database)
        prediction_list = []
        add_matches(db.features_of_type("protein_match"), prediction_list)
        add_matches(db.features_of_type("signalpep"), prediction_list)
        add_matches(db.features_of_type("trans_helix"), prediction_list)
        add_matches(db.features_of_type("PFAM"), prediction_list)
        fout=open(args.json, 'w')
        json.dump(prediction_list,fout)
array=[]
db = gffutils.interface.FeatureDB("test-data/gff.sqlite")

for f in db.all_features():
    dict = {}
    dict['seqid'] = f.seqid
    dict['source'] = f.source
    dict['featuretype'] = f.featuretype
    dict['start'] = f.start
    dict['end'] = f.end
    dict['score'] = f.score
    dict['strand'] = f.strand
    dict['frame'] = f.frame
    dict['attributes']=f.attributes.__dict__["_d"]
    array.append(dict)

fout=open("test-data/gff.json",'w')

json.dump(array,fout)

if __name__ == "__main__":
        main(sys.argv[1:],sys.stdout)
