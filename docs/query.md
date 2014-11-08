# None

None


### `class CoreQuery(profile, metrics=None, dimensions={}, meta=[], title=[])`

TODO:  segment fields userIp / quotaUser


#### ``




#### ``




#### ``




#### `clone()`




#### `daily(start, stop=None, months=1, days=0, precision=0, granularity=None)`




#### ``




#### `dimensions(*dimensions)`




#### `execute()`




#### `filter(value)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `hourly(start, stop=None, months=1, days=0, precision=0, granularity=None)`




#### `limit(*_range)`

Please not carefully that Google Analytics uses  1-indexing on its rows. 


#### `live()`

Turn a regular query into one for the live API. 


#### `metrics(*metrics)`




#### `monthly(start, stop=None, months=1, days=0, precision=0, granularity=None)`




#### `next()`




#### `query(metrics=[], dimensions=[])`




#### `range(start, stop=None, months=1, days=0, precision=0, granularity=None)`




#### `segment(value, type=None)`

E.g. 
query.segment(account.segments['browser']) query.segment('browser') query.segment(account.segments['browser'].any('Chrome', 'Firefox')) 
You can also use the `any`, `all`, `followed_by` and  `immediately_followed_by` functions in this module to  chain together segments. (Experimental.)


#### `set(key=None, value=None, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*columns)`




#### `step(maximum)`

Specify a maximum amount of results to be returned  in any one request, without implying that we should stop  fetching beyond that limit. Useful in debugging pagination functionality, perhaps also when you want to be able to decide whether to continue fetching data, based on the data you've already received. 


#### ``




#### `weekly(start, stop=None, months=1, days=0, precision=0, granularity=None)`




#### `yearly(start, stop=None, months=1, days=0, precision=0, granularity=None)`






### `class Query()`




#### `__init__(profile, metrics=None, dimensions={}, meta=[], title=[])`




#### `clone()`




#### ``




#### `dimensions(*dimensions)`




#### `filter(value)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `metrics(*metrics)`




#### `query(metrics=[], dimensions=[])`




#### `set(key=None, value=None, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*columns)`




#### ``






### `class RealTimeQuery()`




#### `__init__(profile, metrics=None, dimensions={}, meta=[], title=[])`




#### `clone()`




#### ``




#### `dimensions(*dimensions)`




#### `filter(value)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `metrics(*metrics)`




#### `query(metrics=[], dimensions=[])`




#### `set(key=None, value=None, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*columns)`




#### ``






### `class Report()`




#### `__init__(raw, query)`




#### `append(raw, query)`




#### `serialize()`






### `function all(*values)`




### `function any(*values)`




### `function condition(value)`




### `function deepcopy(x, memo=[], _nil=None)`

Deep copy operation on arbitrary Python objects. 
See the module's __doc__ string for more info.


### `function followed_by(*values)`




### `function immediately_followed_by(*values)`




### `function sequence(value)`




