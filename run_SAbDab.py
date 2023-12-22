import pymesh
import argparse
import pdb
import os

from utils import read_config, get_date
from data_prepare.data_prepare import extract_ppi_lists, download, build_blast, ab_contact_map, get_processed_patches, prepare_masif
from time import time
#from blast_search.blast_search import run_blast
#from blast_search.blast_filter import blast_filter, report_hits
#from deep_learning.evaluate_binding import evaluate_binding, filter_MaSIF, compute_native_scores
#from deep_learning.compute_descriptors import compute_descriptors
#from structural_alignment.structural_alignment import structural_alignment, filter_rmsd

parser = argparse.ArgumentParser()

#parser.add_argument('--config', help='optional config file')
parser.add_argument('--reverse', default=False, action="store_true", help='If set True, reverse target and database lists.')
#parser.add_argument('--skip_blast', default=False, action="store_true", help='If set True, skip "Blast search part".')
parser.add_argument('--skip_sabdab', default=False, action="store_true", help='If set True, do not download SAbDab".')
parser.add_argument('--output_dir', help='Output folder for pickles')
parser.add_argument('--input_dir', help='Input directory for experiment')

args = parser.parse_args()
reverse_flag = args.reverse


start = time()
args.config = False
config = read_config(args)
input_dir = args.input_dir
output_dir = args.output_dir

config['input']['sabdab_summary'] = args.input_dir+"/metadata/sabdab_summary_all.tsv"

config['dirs']['lists'] = args.input_dir+"/lists/"
config['dirs']['output'] = args.input_dir+"/output/"
config['out_files']['raw_blast_hits'] = config['dirs']['output'] + '1-raw_blast_hits.tsv'
config['out_files']['filtered_blast_hits'] = config['dirs']['output'] + '2-filtered_blast_hits.tsv'
config['out_files']['TM_align_all'] = config['dirs']['output'] + '3-TM_align.tsv'
config['out_files']['TM_align_filtered'] = config['dirs']['output'] + '3-TM_align_filtered.tsv'
config['out_files']['MaSIF_scores'] = config['dirs']['output'] + '4-DL_scores.tsv'
config['out_files']['MaSIF_scores_filtered'] = config['dirs']['output'] + '4-DL_scores_filtered.tsv'



config['dirs']['data_prepare'] = args.input_dir+"/data_preparation/"

config['dirs']['raw_pdb'] = config['dirs']['data_prepare'] + '00-raw_pdbs/'
config['dirs']['protonated_pdb'] = config['dirs']['data_prepare'] + '01-protonated_pdb/'
config['dirs']['fasta'] = config['dirs']['data_prepare'] + '02-AG_fasta/' # directory with FASTA files of antigens
config['dirs']['fasta_maps'] = config['dirs']['data_prepare'] + '02-AG_fasta_maps/' # files that maps fasta sequences with residue ID
config['dirs']['blast_db'] = config['dirs']['data_prepare'] + '03-blast_db/'
config['dirs']['ab_contact_map'] = config['dirs']['data_prepare'] + '04-ab_contact_map/'

config['dirs']['masif_path'] = '/masif/'
config['dirs']['chains_pdb'] = config['dirs']['data_prepare'] + '05-chains_pdbs/'
config['dirs']['surface_ply'] = config['dirs']['data_prepare'] + '06-surface_ply/'
config['dirs']['patches'] = config['dirs']['data_prepare'] + '07-patches/'
# config['dirs']['dssp_maps'] = config['dirs']['data_prepare'] + '05-dssp_maps/'
config['dirs']['map_patch'] = config['dirs']['data_prepare'] + "08-patch_maps/"



config['dirs']['blast_hits'] = args.input_dir+"/blast_hits/"
config['dirs']['raw_blast_hits'] = config['dirs']['blast_hits'] + '00-raw_hits/' #dir with xml files
#config['dirs']['raw_blast_hits_txt'] = config['dirs']['blast_hits'] + '00-raw_hits_txt/'
config['dirs']['blast_hits_filtered'] = config['dirs']['blast_hits'] + '01-hits_filtered/'



config['dirs']['motifs_pdb'] = args.input_dir+"/motif_pdbs/"
config['dirs']['descriptors'] = config['dirs']['data_prepare'] + '09-descriptors/'
config['dirs']['masif_model'] = config['dirs']['masif_path'] + "data/masif_ppi_search/nn_models/sc05/all_feat/model_data/"

for dir in config['dirs'].values():
    if not os.path.exists(dir):
        os.makedirs(dir)

config['dirs']['tmp'] = args.input_dir+"/tmp/"
config['db_list'] = config['dirs']['lists']+ 'db.txt'
config['target_list'] = config['dirs']['lists'] + 'target.txt'
config['db_list_processed'] = args.input_dir+"/lists/db_processed.txt"
config['target_list_processed'] = args.input_dir+'/lists/target_processed.txt'


if "min_seq_len_target" in config['input'].keys():
    min_seq_len = config['input']['min_seq_len_target']
else:
    min_seq_len=None

#
if not args.skip_sabdab:
    ppi_list_db, ppi_list_target = extract_ppi_lists(config, reverse_flag)
else:
    ppi_list_db = [x.strip('\n') for x in open(config['db_list']).readlines()]
    ppi_list_target = [x.strip('\n') for x in open(config['target_list']).readlines()]
#
updated_ppi_list_db = download(ppi_list_db, config, to_write=config['db_list'], min_seq_len=None)
updated_ppi_list_target = download(ppi_list_target, config, to_write=config['target_list'], min_seq_len=min_seq_len)

import pickle
db = open(output_dir+"/database.sabdab.pkl", "wb")
target = open(output_dir+"/targets.sabdab.pkl", "wb")
pickle.dump(updated_ppi_list_db, db)
pickle.dump(updated_ppi_list_target, target)
