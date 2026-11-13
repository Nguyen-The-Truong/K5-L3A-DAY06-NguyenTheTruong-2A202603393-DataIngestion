"""Writes benchmark/questions.json.

The 24 questions were written by reading the corpus text BEFORE any retrieval was run.
Split rule (fixed before running): dev and test cover different topics inside the two
chapters; test = sampling techniques, compression, IQR/z-score outliers, complement and
range of probability, log transform. Leakage risk: neighbouring topics share a section
(e.g. d16/d10 vs t01/t02 for sampling, d14 vs t06/t07 for probability).
Filter values (section / chapter) are given as an assumed user context before retrieval.
"""
import json
from pathlib import Path

D = "pds-openstax-2025"


def q(id, split, typ, question, ans, page, quote, flt=None, topic=""):
    return dict(id=id, split=split, type=typ, topic=topic, question=question, expected_answer=ans,
                gold_source_id=D, gold_page=page, evidence_quote=quote, filter=flt)


Q = [
    q("d01", "dev", "direct", "What is observational data and how is it collected?",
      "Data collected by systematically observing and recording behavior without the researcher actively participating.",
      68, "Observational data, often used in qualitative research, is collected by systematically observing and recording behavior without the active participation of the researcher.", topic="2.1 data types"),
    q("d02", "dev", "paraphrase", "What kind of data covers customer purchases, website clicks and user interactions?",
      "Transactional data.", 69,
      "It can include financial data, but it also includes data related to customer purchases, website clicks, user interactions, or any other type of activity that is recorded and tracked.", topic="2.1 data types"),
    q("d03", "dev", "direct", "What went wrong with the 1936 Literary Digest poll?",
      "Its mailing list of phone and car owners was biased toward affluent individuals, so it favored Republican voters.",
      72, "This approach was considered biased toward affluent individuals and therefore favored Republican voters.", topic="2.2 survey bias"),
    q("d04", "dev", "conditional", "Why should a survey questionnaire be pilot tested before it is administered widely?",
      "A pilot test with a small group from the target population reveals problems or confusion in the questions so they can be fixed.",
      71, "the survey questionnaire should undergo a pilot test with a small group of individuals from the target population", topic="2.2 survey design"),
    q("d05", "dev", "direct", "What is an application programming interface (API)?",
      "A set of protocols, tools and definitions for building software applications that lets different systems communicate.",
      76, "An application programming interface (API) is a set of protocols, tools, and definitions for building software applications", topic="2.3 APIs"),
    q("d06", "dev", "paraphrase", "Which web scraping technique is useful for extracting dates, phone numbers or email addresses?",
      "Regular expressions.", 77,
      "Useful for scraping data that follows a particular format, such as dates, phone numbers, or email addresses", topic="2.3 scraping techniques"),
    q("d07", "dev", "direct", "What does MCAR mean for missing data?",
      "Missing completely at random: missing data not related to any other variables, with no underlying cause for its absence.",
      87, "MCAR (missing completely at random) data is missing data not related to any other variables, with no underlying cause for its absence.", topic="2.4 missing data"),
    q("d08", "dev", "conditional", "Why should outliers be removed before applying the normalization formula?",
      "Outliers can significantly affect the minimum and maximum values used to scale the data.",
      91, "it is important to first remove any outliers from the dataset before performing normalization", topic="2.4 normalization"),
    q("d09", "dev", "direct", "How does data chunking improve fault tolerance?",
      "If data is corrupted or lost, only the affected chunk has to be retrieved rather than the entire dataset.",
      100, "data chunking allows for the retrieval of only the affected chunk rather than the entire dataset", topic="2.5 chunking"),
    q("d10", "dev", "direct", "What is the difference between sample data and population data?",
      "Population data covers all outcomes of interest; sample data is collected from a subset of the population.",
      115, "Sample data represents outcomes or measurements collected from a subset, or part, of the population of interest.", topic="3.1 sample vs population"),
    q("d11", "dev", "filter", "Which measure of the center is used when outliers skew the mean?",
      "The trimmed mean.", 114,
      "In these instances, the trimmed mean is often used to provide a more representative measure of the center of the dataset",
      {"section": "3.1"}, topic="3.1 outliers (confusable with 2.4, 3.3)"),
    q("d12", "dev", "direct", "Why is the range a weak measure of variation?",
      "It uses only the minimum and maximum, and outliers can skew it.", 121,
      "the range is influenced by outliers since an outlier might appear as a minimum or maximum data value and thus skew the results", topic="3.2 range"),
    q("d13", "dev", "paraphrase", "Why is it not enough to report only the mean of a dataset?",
      "Datasets with the same mean can have very different spread, so a measure of variation is also needed.", 121,
      "publishing the mean of a dataset is often inadequate to fully communicate the characteristics of the dataset", topic="3.2 variation"),
    q("d14", "dev", "direct", "What is the sample space in a probability experiment?",
      "The set of all possible outcomes.", 130,
      "The sample space is the set of all possible outcomes in a probability experiment.", topic="3.4 terminology"),
    q("d15", "dev", "filter", "How can outliers be identified?",
      "With visualizations such as scatterplots, box plots, IQR or histograms, or statistics such as mean, median and standard deviation.",
      87, "This can be done through visualization techniques, such as scatterplots, box plots, IQR (interquartile range), or histograms",
      {"section": "2.4"}, topic="2.4 outliers (confusable with 3.1, 3.3)"),
    q("d16", "dev", "filter", "What is sampling?",
      "Selecting a subset of a larger population to represent and analyze that population.", 71,
      "Sampling is the process of selecting a subset of a larger population to represent and analyze information about that population.",
      {"chapter": 2}, topic="2.2 sampling (confusable with 3.1)"),
    q("t01", "test", "direct", "What is stratified sampling?",
      "Splitting the population into subgroups and taking a random sample from each stratum in proportion to its size.",
      73, "Stratified sampling involves splitting the population into subgroups based on specified factors, such as age, area, income, or education level, and taking a random sample from each stratum in proportion to its size in the population.", topic="2.2 sampling techniques"),
    q("t02", "test", "conditional", "What is the main drawback of convenience sampling?",
      "It may not be representative because it is prone to selection bias.", 73,
      "However, it may not provide a representative sample as it is prone to selection bias", topic="2.2 sampling techniques"),
    q("t03", "test", "paraphrase", "Which type of data compression permanently removes data considered irrelevant or redundant?",
      "Lossy compression.", 98,
      "Lossy compression reduces the size of data by permanently extracting particular data that is considered irrelevant or redundant.", topic="2.5 compression"),
    q("t04", "test", "filter", "What cutoff value is typically used with the IQR to identify outliers?",
      "1.5.", 127, "These formulas typically use 1.5 as a cutoff value to identify outliers in a dataset.",
      {"section": "3.3"}, topic="3.3 IQR outliers (confusable with 2.4)"),
    q("t05", "test", "filter", "Which z-score values are used to flag outliers?",
      "A z-score less than -3 or greater than +3.", 128,
      "greater than +3 can be used to flag outliers", {"section": "3.3"}, topic="3.3 z-scores"),
    q("t06", "test", "direct", "How do you find the probability of the complement of an event?",
      "Subtract the probability of the event from 1.", 131,
      "subtract the probability of Event from 1", topic="3.4 complement"),
    q("t07", "test", "paraphrase", "Can a probability be greater than 1 or negative?",
      "No; a probability must be between 0 and 1 inclusive.", 131,
      "A probability greater than 1 is not possible, and a negative probability is not possible.", topic="3.4 probability range"),
    q("t08", "test", "conditional", "When is a log transformation typically used?",
      "When the data is highly skewed.", 92,
      "Log transformation is often used when the data is highly skewed", topic="2.4 transformation"),
]

if __name__ == "__main__":
    out = Path(__file__).with_name("questions.json")
    out.write_text(json.dumps(Q, indent=2, ensure_ascii=False), encoding="utf-8")
    print(len(Q), "questions;", sum(x["split"] == "dev" for x in Q), "dev;",
          sum(x["split"] == "test" for x in Q), "test;", sum(bool(x["filter"]) for x in Q), "with filter")
