import sys
import os
import gffutils
import argparse




def main(argv, wayout):
        if not len(argv):
                argv.append("-h")
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
        parser.add_argument('-m','--genemap', help="mapping of genes to transcripts")
        parser.add_argument('-p','--peptides',required=True, help="peptide prediction gff")
        parser.add_argument('-b','--blastp', help="blastp outfmt6 results for peptides")
        parser.add_argument('-x','--blastx', help="blastx outfmt6 results for transcripts")
        parser.add_argument('-f','--pfam', help="hmmer results for peptides")
        parser.add_argument('-t','--tmhmm', help="tmhmm results for peptides")
        parser.add_argument('-s','--signalP', help="signalP results for peptides")
        parser.add_argument('-d','--database', required=True, help="gff database to load or create")
        parser.add_argument('-o','--output', required=True, help="output in gff format")
        args = parser.parse_args(argv)


        db = gffutils.create_db(args.peptides, dbfn=args.database, force=True, keep_order=True,merge_strategy='merge', sort_attribute_values=True)
        if args.blastp is not None:
            os.system("convert2gff.py -i "+args.blastp+" -g  "+args.peptides+" -S -p blastp -t protein_match -T  -x > blastp.gff")
            db=db.update("blastp.gff")
        if args.signalP is not None:
            os.system("convert2gff.py -i "+args.signalP+" -g "+args.peptides+" -T -p signalP -t signalpep > signalp.gff")
            db=db.update("signalP.gff")
        if args.tmhmm is not None:
            os.system("convert2gff.py -i "+args.tmhmm+" -g "+args.peptides+" -T -p tmhmm -t trans_helix > tmhmm.gff")
            db=db.update("tmhmm.gff")
        if args.pfam is not None:
            os.system("pfam2gff.py -i "+args.pfam+" -g "+args.peptides+" -T > PFAM.gff")
            db=db.update("PFAM.gff")

        with open(args.output, 'w') as fout:
            for f in db.all_features():
                fout.write(str(f) + '\n')
if __name__ == "__main__":
        main(sys.argv[1:],sys.stdout)
