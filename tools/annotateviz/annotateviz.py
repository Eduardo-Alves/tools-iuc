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
        parser.add_argument('-j','--json', help="annotations in json format")
        parser.add_argument('-p','--pred', help="predictions in json")
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
        # create json for protein predictions
        array=[]
        for f in db.features_of_type("gene"):
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
            for c in db.children(f):
                dict = {}
                dict['seqid'] = c.seqid
                dict['source'] = c.source
                dict['featuretype'] = c.featuretype
                dict['start'] = c.start
                dict['end'] = c.end
                dict['score'] = c.score
                dict['strand'] = c.strand
                dict['frame'] = c.frame
                dict['attributes'] = c.attributes.__dict__["_d"]
                array.append(dict)
        fout2=open(args.pred,'w')
        json.dump(array,fout2)

if __name__ == "__main__":
        main(sys.argv[1:],sys.stdout)
