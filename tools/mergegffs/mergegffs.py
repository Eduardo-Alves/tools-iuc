import sys
import gffutils
import argparse



def main(argv, wayout):
        if not len(argv):
                argv.append("-h")
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
        parser.add_argument('-m','--genemap', help="mapping of genes to transcripts")
        parser.add_argument('-p','--peptides', help="peptide prediction gff")
        parser.add_argument('-a','--annotation', help="annotation gff with protein coordinates",nargs="*")
        parser.add_argument('-d','--database', help="gff database to load or create")
        args = parser.parse_args(argv)
        db = gffutils.create_db(args.peptides, dbfn=args.database, force=True, keep_order=True,merge_strategy='merge', sort_attribute_values=True)
        for gfffile in args.annotation:
                db=db.update(gfffile)
if __name__ == "__main__":
        main(sys.argv[1:],sys.stdout)
