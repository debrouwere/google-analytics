# None

None


### `class CoreQuery(profile, metrics=None, dimensions={}, meta=[], title=[])`

CoreQuery is the main way through which to produce reports from data in Google Analytics. 
The most important methods are: 
* `metrics` and `dimensions` (both of which you can also pass as    lists when creating the query) * `range` and its shortcuts that have the granularity already set:    `hourly`, `daily`, `weekly`, `monthly`, `yearly` * `filter` to filter which rows are analyzed before running the query * `segment` to filter down to a certain kind of session or user (as    opposed to `filter` which works on individual rows of data) * `limit` to ask for a subset of results * `sort` to sort the query 

CoreQuery is mostly immutable: wherever possible, methods  return a new query rather than modifying the existing one, so for example this works as you'd expect it to: 
```python base = profile.query('pageviews') january = base.daily('2014-01-01', months=1).execute() february = base.daily('2014-02-01', months=1).execute() ```


#### ``




#### ``




#### ``




#### `clone()`




#### `daily(start, stop=None, months=1, days=0, precision=0, granularity=None)`

Return a new query that fetches metrics within a certain date range. 
```python query.range('2014-01-01', '2014-06-30') ``` 
If you don't specify a `stop` argument, the date range will end today. If instead  you meant to fetch just a single day's results, try:  
```python query.range('2014-01-01', days=1) ``` 
More generally, you can specify that you'd like a certain number of days,  starting from a certain date: 
```python query.range('2014-01-01', months=3) query.range('2014-01-01', days=28) ``` 
Note that if you don't specify a granularity (either through the `granularity` argument or through the `hourly`, `daily`, `weekly`, `monthly` or `yearly` shortcut methods) you will get only a single result, encompassing the  entire date range, per metric. 
For queries that should run faster, you may specify a lower precision,  and for those that need to be more precise, a higher precision: 
``` # faster queries query.range('2014-01-01', '2014-01-31', precision=0) query.range('2014-01-01', '2014-01-31', precision='FASTER') # queries with the default level of precision (usually what you want) query.range('2014-01-01', '2014-01-31') query.range('2014-01-01', '2014-01-31', precision=1) query.range('2014-01-01', '2014-01-31', precision='DEFAULT') # queries that are more precise query.range('2014-01-01', '2014-01-31', precision=2) query.range('2014-01-01', '2014-01-31', precision='HIGH_PRECISION')         ``` 
**Note:** it is currently not possible to easily specify that you'd like  to query the last last full week or weeks. This will be added sometime in the future. 
As a stopgap measure, it is possible to use the [`nDaysAgo` format][query] format for your start date. 
[query]: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary


#### ``




#### `dimensions(*dimensions)`

Return a new query with additional dimensions. 
```python query.dimensions('search term', 'search depth') ```


#### `execute()`

Run the query and return a `Report`. 
Execute transparently handles paginated results, so even for results that  are larger than the maximum amount of rows the Google Analytics API will  return in a single request, or larger than the amount of rows as specified  through `CoreQuery#step`,  execute will leaf through all pages,   concatenate the results and produce a single Report instance.


#### `filter(value)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `hourly(start, stop=None, months=1, days=0, precision=0, granularity=None)`

Return a new query that fetches metrics within a certain date range. 
```python query.range('2014-01-01', '2014-06-30') ``` 
If you don't specify a `stop` argument, the date range will end today. If instead  you meant to fetch just a single day's results, try:  
```python query.range('2014-01-01', days=1) ``` 
More generally, you can specify that you'd like a certain number of days,  starting from a certain date: 
```python query.range('2014-01-01', months=3) query.range('2014-01-01', days=28) ``` 
Note that if you don't specify a granularity (either through the `granularity` argument or through the `hourly`, `daily`, `weekly`, `monthly` or `yearly` shortcut methods) you will get only a single result, encompassing the  entire date range, per metric. 
For queries that should run faster, you may specify a lower precision,  and for those that need to be more precise, a higher precision: 
``` # faster queries query.range('2014-01-01', '2014-01-31', precision=0) query.range('2014-01-01', '2014-01-31', precision='FASTER') # queries with the default level of precision (usually what you want) query.range('2014-01-01', '2014-01-31') query.range('2014-01-01', '2014-01-31', precision=1) query.range('2014-01-01', '2014-01-31', precision='DEFAULT') # queries that are more precise query.range('2014-01-01', '2014-01-31', precision=2) query.range('2014-01-01', '2014-01-31', precision='HIGH_PRECISION')         ``` 
**Note:** it is currently not possible to easily specify that you'd like  to query the last last full week or weeks. This will be added sometime in the future. 
As a stopgap measure, it is possible to use the [`nDaysAgo` format][query] format for your start date. 
[query]: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary


#### `limit(*_range)`

Return a new query, limited to a certain number of results. 
```python # first 100 query.limit(100) # 50 to 60 query.limit(50, 10) ``` 
Please note carefully that Google Analytics uses  1-indexing on its rows.


#### `live()`

Turn a regular query into one for the live API. 
**Note:** a placeholder, not implemented yet.


#### `metrics(*metrics)`

Return a new query with additional metrics. 
```python query.metrics('pageviews', 'page load time') ```


#### `monthly(start, stop=None, months=1, days=0, precision=0, granularity=None)`

Return a new query that fetches metrics within a certain date range. 
```python query.range('2014-01-01', '2014-06-30') ``` 
If you don't specify a `stop` argument, the date range will end today. If instead  you meant to fetch just a single day's results, try:  
```python query.range('2014-01-01', days=1) ``` 
More generally, you can specify that you'd like a certain number of days,  starting from a certain date: 
```python query.range('2014-01-01', months=3) query.range('2014-01-01', days=28) ``` 
Note that if you don't specify a granularity (either through the `granularity` argument or through the `hourly`, `daily`, `weekly`, `monthly` or `yearly` shortcut methods) you will get only a single result, encompassing the  entire date range, per metric. 
For queries that should run faster, you may specify a lower precision,  and for those that need to be more precise, a higher precision: 
``` # faster queries query.range('2014-01-01', '2014-01-31', precision=0) query.range('2014-01-01', '2014-01-31', precision='FASTER') # queries with the default level of precision (usually what you want) query.range('2014-01-01', '2014-01-31') query.range('2014-01-01', '2014-01-31', precision=1) query.range('2014-01-01', '2014-01-31', precision='DEFAULT') # queries that are more precise query.range('2014-01-01', '2014-01-31', precision=2) query.range('2014-01-01', '2014-01-31', precision='HIGH_PRECISION')         ``` 
**Note:** it is currently not possible to easily specify that you'd like  to query the last last full week or weeks. This will be added sometime in the future. 
As a stopgap measure, it is possible to use the [`nDaysAgo` format][query] format for your start date. 
[query]: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary


#### `next()`

Return a new query with a modified `start_index`. Mainly used internally to paginate through results.


#### `query(metrics=[], dimensions=[])`




#### `range(start, stop=None, months=1, days=0, precision=0, granularity=None)`

Return a new query that fetches metrics within a certain date range. 
```python query.range('2014-01-01', '2014-06-30') ``` 
If you don't specify a `stop` argument, the date range will end today. If instead  you meant to fetch just a single day's results, try:  
```python query.range('2014-01-01', days=1) ``` 
More generally, you can specify that you'd like a certain number of days,  starting from a certain date: 
```python query.range('2014-01-01', months=3) query.range('2014-01-01', days=28) ``` 
Note that if you don't specify a granularity (either through the `granularity` argument or through the `hourly`, `daily`, `weekly`, `monthly` or `yearly` shortcut methods) you will get only a single result, encompassing the  entire date range, per metric. 
For queries that should run faster, you may specify a lower precision,  and for those that need to be more precise, a higher precision: 
``` # faster queries query.range('2014-01-01', '2014-01-31', precision=0) query.range('2014-01-01', '2014-01-31', precision='FASTER') # queries with the default level of precision (usually what you want) query.range('2014-01-01', '2014-01-31') query.range('2014-01-01', '2014-01-31', precision=1) query.range('2014-01-01', '2014-01-31', precision='DEFAULT') # queries that are more precise query.range('2014-01-01', '2014-01-31', precision=2) query.range('2014-01-01', '2014-01-31', precision='HIGH_PRECISION')         ``` 
**Note:** it is currently not possible to easily specify that you'd like  to query the last last full week or weeks. This will be added sometime in the future. 
As a stopgap measure, it is possible to use the [`nDaysAgo` format][query] format for your start date. 
[query]: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary


#### `segment(value, type=None)`

Return a new query, limited to a segment of all users or sessions. 
Accepts segment objects, filtered segment objects and segment names: 
```python query.segment(account.segments['browser']) query.segment('browser') query.segment(account.segments['browser'].any('Chrome', 'Firefox')) ``` 
Segment can also accept a segment expression when you pass  in a `type` argument. The type argument can be either `users` or `sessions`. This is pretty close to the metal. 
```python # will be translated into `users::condition::perUser::ga:sessions>10` query.segment('condition::perUser::ga:sessions>10', type='users') ``` 
See the [Google Analytics dynamic segments documentation][segments] 
You can also use the `any`, `all`, `followed_by` and  `immediately_followed_by` functions in this module to  chain together segments. 
Everything about how segments get handled is still in flux. Feel free to propose ideas for a nicer interface on  the [GitHub issues page][issues] 
[segments]: https://developers.google.com/analytics/devguides/reporting/core/v3/segments#reference [issues]: https://github.com/debrouwere/google-analytics/issues


#### `set(key=None, value=None, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*columns)`

Return a new query which will produce results sorted by  one or more metrics or dimensions. You may use plain  strings for the columns, or actual `Column`, `Metric`  and `Dimension` objects. 
Add a minus in front of the metric (either the string or  the object) to sort in descending order. 
```python # sort using strings query.sort('pageviews', '-device type') 
# sort using metric, dimension or column objects pageviews = account.metrics['pageviews'] query.sort(-pageviews) ```


#### `step(maximum)`

Return a new query with a maximum amount of results to be returned  in any one request, without implying that we should stop  fetching beyond that limit (unlike `CoreQuery#limit`.) 
Useful in debugging pagination functionality. 
Perhaps also useful when you  want to be able to decide whether to continue fetching data, based  on the data you've already received.


#### ``




#### `weekly(start, stop=None, months=1, days=0, precision=0, granularity=None)`

Return a new query that fetches metrics within a certain date range. 
```python query.range('2014-01-01', '2014-06-30') ``` 
If you don't specify a `stop` argument, the date range will end today. If instead  you meant to fetch just a single day's results, try:  
```python query.range('2014-01-01', days=1) ``` 
More generally, you can specify that you'd like a certain number of days,  starting from a certain date: 
```python query.range('2014-01-01', months=3) query.range('2014-01-01', days=28) ``` 
Note that if you don't specify a granularity (either through the `granularity` argument or through the `hourly`, `daily`, `weekly`, `monthly` or `yearly` shortcut methods) you will get only a single result, encompassing the  entire date range, per metric. 
For queries that should run faster, you may specify a lower precision,  and for those that need to be more precise, a higher precision: 
``` # faster queries query.range('2014-01-01', '2014-01-31', precision=0) query.range('2014-01-01', '2014-01-31', precision='FASTER') # queries with the default level of precision (usually what you want) query.range('2014-01-01', '2014-01-31') query.range('2014-01-01', '2014-01-31', precision=1) query.range('2014-01-01', '2014-01-31', precision='DEFAULT') # queries that are more precise query.range('2014-01-01', '2014-01-31', precision=2) query.range('2014-01-01', '2014-01-31', precision='HIGH_PRECISION')         ``` 
**Note:** it is currently not possible to easily specify that you'd like  to query the last last full week or weeks. This will be added sometime in the future. 
As a stopgap measure, it is possible to use the [`nDaysAgo` format][query] format for your start date. 
[query]: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary


#### `yearly(start, stop=None, months=1, days=0, precision=0, granularity=None)`

Return a new query that fetches metrics within a certain date range. 
```python query.range('2014-01-01', '2014-06-30') ``` 
If you don't specify a `stop` argument, the date range will end today. If instead  you meant to fetch just a single day's results, try:  
```python query.range('2014-01-01', days=1) ``` 
More generally, you can specify that you'd like a certain number of days,  starting from a certain date: 
```python query.range('2014-01-01', months=3) query.range('2014-01-01', days=28) ``` 
Note that if you don't specify a granularity (either through the `granularity` argument or through the `hourly`, `daily`, `weekly`, `monthly` or `yearly` shortcut methods) you will get only a single result, encompassing the  entire date range, per metric. 
For queries that should run faster, you may specify a lower precision,  and for those that need to be more precise, a higher precision: 
``` # faster queries query.range('2014-01-01', '2014-01-31', precision=0) query.range('2014-01-01', '2014-01-31', precision='FASTER') # queries with the default level of precision (usually what you want) query.range('2014-01-01', '2014-01-31') query.range('2014-01-01', '2014-01-31', precision=1) query.range('2014-01-01', '2014-01-31', precision='DEFAULT') # queries that are more precise query.range('2014-01-01', '2014-01-31', precision=2) query.range('2014-01-01', '2014-01-31', precision='HIGH_PRECISION')         ``` 
**Note:** it is currently not possible to easily specify that you'd like  to query the last last full week or weeks. This will be added sometime in the future. 
As a stopgap measure, it is possible to use the [`nDaysAgo` format][query] format for your start date. 
[query]: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary




### `class Query()`




#### `__init__(profile, metrics=None, dimensions={}, meta=[], title=[])`




#### `clone()`




#### ``




#### `dimensions(*dimensions)`

Return a new query with additional dimensions. 
```python query.dimensions('search term', 'search depth') ```


#### `filter(value)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `metrics(*metrics)`

Return a new query with additional metrics. 
```python query.metrics('pageviews', 'page load time') ```


#### `query(metrics=[], dimensions=[])`




#### `set(key=None, value=None, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*columns)`

Return a new query which will produce results sorted by  one or more metrics or dimensions. You may use plain  strings for the columns, or actual `Column`, `Metric`  and `Dimension` objects. 
Add a minus in front of the metric (either the string or  the object) to sort in descending order. 
```python # sort using strings query.sort('pageviews', '-device type') 
# sort using metric, dimension or column objects pageviews = account.metrics['pageviews'] query.sort(-pageviews) ```


#### ``






### `class RealTimeQuery()`

A query against the [Google Analytics Live API][live]. 
**Note:** a placeholder, not implemented yet. 
[live]: https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/data/realtime#resource


#### `__init__(profile, metrics=None, dimensions={}, meta=[], title=[])`




#### `clone()`




#### ``




#### `dimensions(*dimensions)`

Return a new query with additional dimensions. 
```python query.dimensions('search term', 'search depth') ```


#### `filter(value)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `metrics(*metrics)`

Return a new query with additional metrics. 
```python query.metrics('pageviews', 'page load time') ```


#### `query(metrics=[], dimensions=[])`




#### `set(key=None, value=None, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*columns)`

Return a new query which will produce results sorted by  one or more metrics or dimensions. You may use plain  strings for the columns, or actual `Column`, `Metric`  and `Dimension` objects. 
Add a minus in front of the metric (either the string or  the object) to sort in descending order. 
```python # sort using strings query.sort('pageviews', '-device type') 
# sort using metric, dimension or column objects pageviews = account.metrics['pageviews'] query.sort(-pageviews) ```


#### ``






### `function deepcopy(x, memo=[], _nil=None)`

Deep copy operation on arbitrary Python objects. 
See the module's __doc__ string for more info.


### `function describe(profile, description)`

Generate a query by describing it as a series of actions  and parameters to those actions. These map directly  to Query methods and arguments to those methods. 
This is an alternative to the chaining interface. Mostly useful if you'd like to put your queries in a file, rather than in Python code.


### `function refine(query, description)`

Refine a query from a dictionary of parameters that describes it. See `describe` for more information.


