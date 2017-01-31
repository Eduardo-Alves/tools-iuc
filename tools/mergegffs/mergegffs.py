import sys
import gffutils
import argparse



def main(argv, wayout):
        if not len(argv):
                argv.append("-h")
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescription
HelpFormatter, description=__doc__)
	parser.add_argument('-t','--transcriptome', help="transcriptome gff")
	parser.add_argument('-g','--gff', help="gff to add to annotation",nargs="*")

        args = parser.parse_args(argv)
	db = gffutils.create_db(fn, dbfn='test.db', force=True, keep_order=True,merge_strategy='merge', sort_attribute_values=True)
	for gfffile in args.proteingff:
		db=db.update(gfffile)



if __name__ == "__main__":
        main(sys.argv[1:],sys.stdout)

