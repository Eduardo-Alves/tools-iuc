import sys
import os
import gffutils
import argparse
import json

def main(argv, wayout):
        if not len(argv):
                argv.append("-h")
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
        parser.add_argument('-d','--database', help="gffutils sqlite database")
        parser.add_argument('-j','--json', help="report in json format")
        trans_dict={}
        db = gffutils.interface.FeatureDB(args.database)
        transcripts=db.features_of_type("mRNA")
        for t in transcripts:
            trans={}
            trans.len=db.children_bp(t)
            trans.id=t["ID"]
            trans.gene=t["parent"]
            trans.matches=[]
            trans_dict[t["ID"]]=trans{}
        matches=db.features_of_type("protein_match")
        for m in matches:
            trans_dict[m["target"]].matches.append[{"source":m["source"],"start":m["start"]}]

        fout=open(args.json, 'w')
        trans_list=[]
        for t in trans_dict.values():
            trans_list.append(t)
        json.dump(trans_list,fout)
