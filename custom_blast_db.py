# The custom_blast_db.py script takes a fasta file and tries to identify
# each read by blasting it against a reference set of sequences. The script
# uses the blast+ tool to setup a reference database (makeblastdb) and then
# identify the fasta sequences with the blastn tool.


# import the argparse module to handle the input commands

import argparse

# get the arguments that provide the input fasta and reference file, together with the output file.
parser = argparse.ArgumentParser(description = 'create a custom blast database and run a fasta file against it')

parser.add_argument('-i', metavar='fasta file(s)', type=str, 
			help='enter the fasta file that needs to be identified')
parser.add_argument('-o', metavar='output file', type=str, 
			help='enter the output file')
parser.add_argument('-r', metavar='reference file', type=str, 
			help='enter the reference file on wich the blast database will be based')
args = parser.parse_args()

def paths():
	# import modules to run bash commands and read the shell information
	from subprocess import Popen, PIPE
		
	
	# use the linux 'pwd' command to get the working directory
	work_path = Popen(['pwd'], stdout=PIPE)
	work_path = work_path.communicate()[0].replace('\n', '')

	# use the linux 'find' command to find the directory in wich the blast+ files are located
	ncbi_path = Popen(['find', '/home' ,'-name', 'makeblastdb'], stdout=PIPE)
	ncbi_path = ncbi_path.communicate()[0].split('makeblastdb')[0]
	
	return(work_path, ncbi_path)

def make_db (ref_fasta_file, ncbi_path):
	# import module that allows the makeblastdb program to be run
	from subprocess import call
	
	#make a reference database with the makeblastdb tool
	p = call([(ncbi_path + 'makeblastdb'), '-in', ref_fasta_file, 
			'-dbtype', 'nucl', '-parse_seqids', '-hash_index'])

def run_db (sequence_fasta_file, ncbi_path, db_name, outfile):
	# import module that allows the blastn tool to be run
	from subprocess import call

	#run the fasta file against the reference database with the blastn tool
	print('Blasting query file against the database . . .')
	p = call([(ncbi_path + 'blastn'), '-query', sequence_fasta_file, '-db',
			db_name, '-out', outfile, '-evalue', '10', '-outfmt', '10'])
	
def clean_up (db_name):
	# import module that can run bash commands
	from subprocess import call

	#clean up database files with the 'rm' command
	cmd = 'rm ' + db_name + '.*'	
	p = call(cmd, shell = True)

def parse_blast_result (csv_path):
	# parse the blast results to add headers and normalize the output so it is
	# similar to the blast.py output.
	lines = [line for line in open(csv_path, 'r')]
	
	# write the header
	csvfile = open(csv_path, 'w')
	csvfile.write('Blast hit,Sequence,Percentage matched,length match,mismatches,gaps,query start,query end,subject start,subject end,e-value,bitscore\n')
	
	# add quotes around the blast hit, to simplify the importation of the csv file into spreadsheat programs
	for line in lines:
		line = line.split(',')
		info = ','.join(line[-11:])
		blast = '\"' + ','.join(line[:-(len(line)-1)]) + '\"'
		csvfile.write(blast + ',' + info)
		

def main ():
	# make the blast database
	make_db(args.r, paths()[1])
	
	# blast the fasta file against the newly created database
	run_db(args.i, paths()[1], args.r, args.o)

	# remove database files
	clean_up(args.r)
	
	# process output
	parse_blast_result(args.o)	

		
if __name__ == "__main__":
    main()

