import scipy.stats

ranked = [6,10,16,25,26] #second pick ranks
picked = [5,27,8,39,38] #seeding ranks

(r,p) = scipy.stats.pearsonr(ranked,picked)
print r