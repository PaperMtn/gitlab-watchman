# Signatures
GitLab Watchman uses signatures to provide the search terms to query GitLab and Regex patterns to filter out true positives.

They are written in YAML, and follow this format:
```yaml
---
filename:
enabled: #[true|false]
meta:
  name:
  author:
  date:
  description: #what the search should find#
  severity: #rating out of 100#
scope: #what to search, any combination of the below#
- blobs
- commits
- milestones
- wiki_blobs
- issues
- merge_requests
- notes
- snippet_titles
test_cases:
  match_cases:
  - #test case that should match the regex#
  fail_cases:
  - #test case that should not match the regex#
strings:
- #search query to use in GitLab#
pattern: #Regex pattern to filter out false positives#
```

Signatures are stored in the directory src/signatures, so you can see examples there.

**Scope**
This is where GitLab should look:
- blobs
- commits
- milestones
- wiki_blobs
- issues
- merge_requests
- notes
- snippet_titles

You can search for any combination of these, with each on its own line

**Test cases**
These test cases are used to check that the regex pattern works. Each signature should have at least one match (pass) and one fail case.

If you want to return all results found by a query, enter the value `blank` for both cases.

## Creating your own signatures
You can easily create your own signatures for GitLab Watchman. The two most important parts are the search queries and the regex pattern.

### Search queries
These are stored as the entries in the 'strings' section of the signature, and are the search terms used to query GitLab to find results.

Multiple entries can be put under strings to find as many potential hits as you can. So if I wanted to find passwords, I might use both of these search terms:
`- password`
`- password is`

#### Search terminology
The GitLab API, when advanced search is configured, uses Elasticsearch syntax, which is described in full [here](https://docs.gitlab.com/ee/user/search/advanced_search_syntax.html)

Here is an excerpt from the article:
- Searches look for all the words in a query, in any order - e.g.: searching issues for display bug and bug display will return the same results.
- To find the exact phrase (stemming still applies), use double quotes: `"display bug"`
- To find bugs not mentioning display, use -: `bug -display`
- To find a bug in display or banner, use |: `bug display | banner`
- To group terms together, use parentheses: `bug | (display +banner)`
- To match a partial word, use \*. In this example, I want to find bugs with any 500 errors. : `bug error 50*`
- To use one of symbols above literally, escape the symbol with a preceding \: `argument \-last`

Using this syntax, you can build signatures with queries to find very specific files and information.

### Regex pattern
This pattern is used to filter results that are returned by the search query.

If you want to return all results found by a query, enter the value `''` for the pattern.
