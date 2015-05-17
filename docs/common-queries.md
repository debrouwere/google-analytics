# Common Queries

This page mirrors the "Common Queries" page from the official Google Analytics documentation, with queries translated into Python. Query descriptions are copied verbatim from there.

([Open a GitHub issue](https://github.com/debrouwere/google-analytics/issues/new) if you'd like to see the equivalent queries on the command-line.)

All queries below build on a basic query for daily data from the last 30 days: 

```python
import googleanalytics as ga
accounts = ga.authenticate()
profile = accounts[0].webproperties[0].profile
query = profile.core.query().daily(months=-1)
```

To learn more about authentication or how to work with reports (the output of these queries), take a look at the [README](https://github.com/debrouwere/google-analytics/blob/master/README.md) first.

## General queries

### Users and Pageviews Over Time

This query returns the total users and pageviews for the specified time period. Note that this query doesn't require any dimensions.

```python
query.metrics('sessions', 'pageviews')
```

### Mobile traffic

This query returns some information about sessions which occurred from mobile devices. Note that "Mobile Traffic" is defined using the default segment ID -14.

```python
query \
    .metrics('sessions', 'pageviews', 'session duration') \
    .dimensions('mobile device info', 'source') \
    .segment('mobile traffic')
```

### Revenue Generating Campaigns

This query returns campaign and site usage data for campaigns that led to more than one purchase through your site.

```python
# note: the dynamic segmentation interface is pretty close to the metal, 
# but will likely be improved in the future
query \
    .metrics('sessions', 'pageviews', 'session duration', 'bounces') \
    .dimensions('source', 'medium') \
    .segment('dynamic::ga:transactions>1')
```

## Users

### New vs Returning Sessions

This query returns the number of new sessions vs returning sessions.

```python
query \
    .metrics('sessions') \
    .dimensions('user type')
```

### Sessions by Country

This query returns a breakdown of your sessions by country, sorted by number of sessions.

```python
query \
    .metrics('sessions') \
    .dimensions('country') \
    .sort('-sessions')
```

dimensions=ga:country
metrics=ga:sessions
sort=-ga:sessions

### Browser and Operating System

This query returns a breakdown of sessions by the Operating System, web browser, and browser version used.

```python
query \
    .metrics('sessions') \
    .dimensions('operating system', 'operating system version', 'browser', 'browser version')
```

### Time on Site

This query returns the number of sessions and total time on site, which can be used to calculate average time on site.

```python
query \
    .metrics('sessions', 'session duration')
```

## Traffic Sources

### All Traffic Sources - Usage

This query returns the site usage data broken down by source and medium, sorted by sessions in descending order.

```python
query \
    .metrics('sessions', 'pageviews', 'session duration', 'exits') \
    .dimensions('source', 'medium') \
    .sort('sessions', descending=True)
```

### All Traffic Sources - Goals

This query returns data for the first and all goals defined, sorted by total goal completions in descending order.

```python
query \
    .metrics('sessions', 
        'goal 1 starts', 'goal 1 completions', 'goal 1 value', 
        'goal starts', 'goal completions', 'goal value') \
    .dimensions('source', 'medium') \
    .sort('goal completions')
```

dimensions=ga:source,ga:medium
metrics=ga:sessions,ga:goal1Starts,ga:goal1Completions,ga:goal1Value,ga:goalStartsAll,ga:goalCompletionsAll,ga:goalValueAll
sort=-ga:goalCompletionsAll

### All Traffic Sources - E-Commerce

This query returns information on revenue generated through the site for the given time span, sorted by sessions in descending order.

```python
query \
    .metrics
```

dimensions=ga:source,ga:medium
metrics=ga:sessions,ga:transactionRevenue,ga:transactions,ga:uniquePurchases
sort=-ga:sessions

### Referring Sites

This query returns a list of domains and how many sessions each referred to your site, sorted by pageviews in descending order.

```python
query \
    .metrics
```

dimensions=ga:source
metrics=ga:pageviews,ga:sessionDuration,ga:exits
filters=ga:medium==referral
sort=-ga:pageviews

### Search Engines

This query returns site usage data for all traffic by search engine, sorted by pageviews in descending order.

```python
query \
    .metrics
```

dimensions=ga:source
metrics=ga:pageviews,ga:sessionDuration,ga:exits
filters=ga:medium==cpa,ga:medium==cpc,ga:medium==cpm,ga:medium==cpp,ga:medium==cpv,ga:medium==organic,ga:medium==ppc
sort=-ga:pageviews


### Search Engines - Organic Search

This query returns site usage data for organic traffic by search engine, sorted by pageviews in descending order.

```python
query \
    .metrics
```

dimensions=ga:source
metrics=ga:pageviews,ga:sessionDuration,ga:exits
filters=ga:medium==organic
sort=-ga:pageviews

### Search Engines - Paid Search

This query returns site usage data for paid traffic by search engine, sorted by pageviews in descending order.

```python
query \
    .metrics
```

dimensions=ga:source
metrics=ga:pageviews,ga:sessionDuration,ga:exits
filters=ga:medium==cpa,ga:medium==cpc,ga:medium==cpm,ga:medium==cpp,ga:medium==cpv,ga:medium==ppc
sort=-ga:pageviews

### Keywords

This query returns sessions broken down by search engine keywords used, sorted by sessions in descending order.

```python
query \
    .metrics
```

dimensions=ga:keyword
metrics=ga:sessions
sort=-ga:sessions

## Content

### Top Content

This query returns your most popular content, sorted by most pageviews.

```python
query \
    .metrics
```

dimensions=ga:pagePath
metrics=ga:pageviews,ga:uniquePageviews,ga:timeOnPage,ga:bounces,ga:entrances,ga:exits
sort=-ga:pageviews

### Top Landing Pages

This query returns your most popular landing pages, sorted by entrances in descending order.

```python
query \
    .metrics
```

dimensions=ga:landingPagePath
metrics=ga:entrances,ga:bounces
sort=-ga:entrances

### Top Exit Pages

This query returns your most common exit pages, sorted by exits in descending order.

```python
query \
    .metrics
```

dimensions=ga:exitPagePath
metrics=ga:exits,ga:pageviews
sort=-ga:exits

### Site Search - Search Terms

This query returns the number of sessions broken down by internal site search, sorted by number of unique searches for a keyword in descending order.

```python
query \
    .metrics
```

dimensions=ga:searchKeyword
metrics=ga:searchUniques
sort=-ga:searchUniques