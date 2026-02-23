from scipy.stats import mannwhitneyu
import numpy as np

# a12 is reused, sourced from IGDec-QAOA (https://github.com/qiqihannah/IGDec-QAOA)
def a12(lst1,lst2,rev=True):
  "how often is x in lst1 more than y in lst2?"
  more = same = 0.0
  for x in lst1:
    for y in lst2:
      if x==y : same += 1
      elif rev and x > y : more += 1
      elif not rev and x < y : more += 1
  return (more + 0.5*same)  / (len(lst1)*len(lst2))

def nominal_magnitude(a12_val):
  scaled_a12_val = 2 * (a12_val - 0.5)
  abs_a12_val = np.abs(scaled_a12_val)
  if abs_a12_val < 0.147:
    mag = "(N)"   # Negligible
  elif abs_a12_val >= 0.147 and abs_a12_val < 0.33:
    mag = "(S)"   # Small
  elif abs_a12_val >= 0.33 and abs_a12_val < 0.474:
    mag = "(M)"   # Medium
  elif abs_a12_val > 0.474:
    mag = "(L)"   # Large
  return scaled_a12_val, mag

def return_pval_and_effectsize(sample_1, sample_2):
  _, pval = mannwhitneyu(sample_1, sample_2, alternative='two-sided') 
  a12_val =  a12(sample_1, sample_2) # Test whether acc_1 > acc_2 (acc_i involved in sample_i)
  return pval, a12_val