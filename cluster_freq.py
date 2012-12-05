# Go through the list of clusters, and list how many sequences there are present in each cluster and
# from what input file these sequences originate. The script can merge different clusters together
# if they have the same blast hit, with this it possible to combine different markers.

import argparse

# get arguments
parser = argparse.ArgumentParser(description = 'List the fasta sequences present in each cluster')

parser.add_argument('-c', metavar='cluster txt file', type=str, 
			help='enter the cluster text file')
parser.add_argument('-f', metavar='cluster fasta file', type=str, 
			help='enter the cluster fasta file')
parser.add_argument('-t', metavar='tag file', type=str, 
			help='enter the tag file')
parser.add_argument('-o', metavar='output directory', type=str, 
			help='the output directory')
parser.add_argument('-b', metavar='blast file', type=str,
			help='the file with the blast identifications')
parser.add_argument('-s', metavar='minimum OTU size', type=int, 
			help='minimum size for an OTU to be analyzed (default: 10)', default=10)
args = parser.parse_args()

def get_tag (tag_file):
	
	# get the tags that are associated with the fasta files
	return [line.replace('\n', '').split('\t')[0::2] for line in open(tag_file, 'r')]

def get_blast (blast_file):
	
	# parse the blast file and retrieve the identications
	blast_dic, seq_dic, count = {}, {}, 0
	for line in open(blast_file, 'r'):
		if 'Percentage matched' not in line:
			line = line.replace('\"','').replace('\n','').split('\t')
			count += 1
			for i in range(0, len(line)):
				if '_cluster_' in line[i]:
					if len(line) > 15:
						blast_dic[line[i+1]] = line[i:(i+4)]+line[12:16]
					else:
						blast_dic[line[i+1]] = line[i:(i+4)]+['','','','']
					#seq_dic[line[i].split('_cluster_')[0]] = line[i+1]

	print('number of blast hits ' + str(count))
	#return [blast_dic, seq_dic]
	return blast_dic
	
def get_otu (otu_file, min_size):
	
	# return a nested list with all the sequences in the OTU's
	otu_seq_dic = {}
	for line in open(otu_file, 'r'):
		line = line.replace('\n','').split('\t')
		otu_seq_dic[line[0]] = line[1:]
		
	return otu_seq_dic

def get_cluster_name (fasta_file):
	# import the biopython module to process the fasta file
	from Bio import SeqIO
	
	cluster_dic = {}
	
	# parse through the cluster fasta file, and retrieve the cluster name for each otu
	for seq_record in SeqIO.parse(fasta_file, 'fasta'):
		cluster_dic[seq_record.id.split('_cluster')[0]] = seq_record.id
	
	return cluster_dic

def write_result (tag_dic, tag_list, header, blast, out_dir):

	# write the results
	out_file = open(out_dir + 'cluster_input_seqs.csv', 'a')
	if header == 'yes': out_file.write('Cluster\tBlast idenification\tPercentage matched\tlength match\taccession\tgenus\tspecies\ttaxonomy\t' + '\t'.join([item[0] for item in tag_list]) + '\n')
	temp = '\t'.join(blast)
	for item in tag_list:
		try: 
			temp += ('\t' + str(tag_dic[item[1]]))
		except:
			temp += ('\t0')
	out_file.write(temp + '\n')
	
def otu_freq_dist (otu_seqs, tag_list, blast_dic, out_dir):
	
	# retrieve the otu clusters that meet the size restriction
	header = 'yes'
	blast_key = blast_dic.keys()
	
	# go through the blast hit dictionary
	for hit in blast_key:
		tag_dic, blast = {}, blast_dic[hit]
		# obtain the cluster for which the blast hit was obtained		
		cluster = blast_dic[hit][0].split('_cluster_#:')[1].split('_length_')[0]
		# go through the otu sequences and count based on the tag
		# how many sequences there are present from each input dataset
		for seq in otu_seqs[cluster]:
			try:
				tag_dic[seq.split('_')[0]] += 1
			except:
				tag_dic[seq.split('_')[0]] = 1
		# write the results
		write_result(tag_dic, tag_list, header, blast, out_dir)
		header = 'no'		

def main ():
	# get the tags
	tag = get_tag(args.t)
	
	# get the blast information
	blast =  get_blast(args.b)
	
	# get otus sequences
	otu_seqs = get_otu(args.c, args.s)
	
	# get the otu names
	otu_name = get_cluster_name(args.f)
	
	# combine and export the information
	otu_freq_dist(otu_seqs, tag, blast, args.o)
	
if __name__ == "__main__":
    main()

