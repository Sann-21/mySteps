import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    trans_state={}
    con_link = len(corpus[page])

    if con_link:
        for l in corpus:
            trans_state[l] = (1-damping_factor)/len(corpus)
        for l in corpus[page]:
            trans_state[l] += damping_factor/con_link
    else:
        for l in corpus:
            trans_state[l] = 1/len(corpus)
    
    return trans_state




def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sample ={}
    next_page = random.choice(list(corpus))

    for i in range(1,n):
        current_model = transition_model(corpus, next_page, damping_factor)
        next_page = random.choices(list(current_model), current_model.values(), k=1)[0]

        if next_page in sample:
            sample[next_page] += 1
        else:
            sample[next_page]= 1

    for i in sample:
        sample[i]/= n

    return sample

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    rank={}
    new_rank={}
        
    for i in corpus:
        rank[i] = 1/len(corpus)

    flag =True
    while flag:
        for i in rank:
            total = 0
            for j in corpus:
                if i in corpus[j]:
                    total+= rank[j]/len(corpus[j])
                if not corpus[j]:
                    total += rank[j]/len(corpus)

            new_rank[i] =(1-damping_factor)/len(corpus) + damping_factor* total
        flag =False
        for k in rank:
            if not math.isclose(new_rank[k], rank[k], abs_tol=0.001):
                flag=True
            rank[k] = new_rank[k]
    return rank





if __name__ == "__main__":
    main()
