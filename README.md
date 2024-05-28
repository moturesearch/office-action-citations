# office-action-citations
This repository contains code for consolidating office-action citations using OpenAlex (or Crossref when a match wasn’t found with OpenAlex).

## Approach
We outline our approach below. We also provide a pipeline diagram summarising our approach (see below).

We used OpenAlex to consolidate citations. If a citation contained a title, we searched using the title. If a citation did not contain a title (or a match was not found using the title), we followed the steps below. We also followed the step below if the _relevance score_ of a title-matched citation was below 600. We selected 600 as our threshold based on validating a sample of 100 title-matched citations.

-	We filtered out citations that were missing information for first author, journal, or publication year. To ensure a low false positive match rate, we further limited our sample to citations that contained at least one of the following pieces of information: volume number, issue number, first page number, last page number.
-	OpenAlex has a unique identifier for each author and journal. We searched for these unique identifiers, and only proceeded if a unique identifier was found for both the first author and the journal.
-	We used these unique identifiers along with publication year and any extra information (namely, volume number, issue number, first page number, last page number) to search OpenAlex. Because volume number, issue number, and page numbers are not formatted consistently across citations, it possible for Grobid to incorrectly assign these values (_e.g.,_ volume and issue number could be swapped around). For this reason, we searched OpenAlex using all permutations of the values assigned to these four pieces of information. Note that we permuted the values for all fields (even if a value for a given field was missing).
-	Unlike title searches, these searches do not return a relevance score. For this reason, we selected the first result returned by OpenAlex as we are unable to determine the best match in cases where more than one permutation returns a match (this is unlikely given our strict filtering criteria described above).

If a match was not found using OpenAlex, we used Crossref (which can be used via Grobid). Grobid extracts and consolidates citations using Crossref. We sent a reasonably small number of citations to Crossref. This is important because Crossref is unsuitable for processing large numbers of citations. If Crossref was able to consolidate the citation (_i.e.,_ a DOI was found), we sent the DOI to OpenAlex to retrieve the meta-data for the citation.

The pipeline diagram is below. Note that meta-data refers to a citation having information for: author, year, journal, and at least one of volume number, issue number, first or last page number.

![Image Alt text](/images/flowchart_method_v3_crop.jpg)

## Code
Below is a flowchart showing our workflow. The flowchart shows what code files we ran and in what order.

![Image Alt text](/images/ml05_git.jpg)

## Data
Our data is available on figshare.

Office-action citation data. https://doi.org/10.6084/m9.figshare.25874452.v1 

Classification data. https://doi.org/10.6084/m9.figshare.25874464.v1 
