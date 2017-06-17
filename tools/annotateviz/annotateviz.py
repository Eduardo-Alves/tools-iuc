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
        gffutils.constants.always_return_list = False
        db = gffutils.interface.FeatureDB(args.database)
        prediction_list = []
        add_matches(db.features_of_type("protein_match"), prediction_list)
        add_matches(db.features_of_type("signalpep"), prediction_list)
        add_matches(db.features_of_type("trans_helix"), prediction_list)
        add_matches(db.features_of_type("PFAM"), prediction_list)
        fout=open(args.json, 'w')
        json.dump(prediction_list,fout)
