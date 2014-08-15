# None

None


### `class CoreQuery(profile, metrics={}, dimensions=[], meta=[])` 

TODO:  segment fields userIp / quotaUser


#### ``




#### ``




#### ``




#### `clone()`




#### `daily(*vargs, **kwargs)`




#### `execute()`




#### `filter(*vargs, **kwargs)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `hourly(*vargs, **kwargs)`




#### `limit(*vargs, **kwargs)`

Please not carefully that Google Analytics uses  1-indexing on its rows. 


#### `live()`

Turn a regular query into one for the live API. 


#### `monthly(*vargs, **kwargs)`




#### `next(*vargs, **kwargs)`




#### `range(*vargs, **kwargs)`




#### `segment(*vargs, **kwargs)`

E.g. 
query.segment(account.segments['browser']) query.segment('browser') query.segment(account.segments['browser'].any('Chrome', 'Firefox')) 
You can also use the `any`, `all`, `followed_by` and  `immediately_followed_by` functions in this module to  chain together segments. (Experimental.)


#### `set(*vargs, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*vargs, **kwargs)`




#### `specify(*vargs, **kwargs)`




#### `step(*vargs, **kwargs)`

Specify a maximum amount of results to be returned  in any one request, without implying that we should stop  fetching beyond that limit. Useful in debugging pagination functionality, perhaps also when you want to be able to decide whether to continue fetching data, based on the data you've already received. 


#### `weekly(*vargs, **kwargs)`




#### `yearly(*vargs, **kwargs)`






### `class Query()` 




#### `__init__(profile, metrics={}, dimensions=[], meta=[])`




#### `clone()`




#### `filter(*vargs, **kwargs)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `set(*vargs, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*vargs, **kwargs)`




#### `specify(*vargs, **kwargs)`






### `class RealTimeQuery()` 




#### `__init__(profile, metrics={}, dimensions=[], meta=[])`




#### `clone()`




#### `filter(*vargs, **kwargs)`

Most of the actual functionality lives on the Column  object and the `all` and `any` functions. 


#### `set(*vargs, **kwargs)`

`set` is a way to add raw properties to the request,  for features that python-google-analytics does not  support or supports incompletely. For convenience's  sake, it will serialize Column objects but will  leave any other kind of value alone.


#### `sort(*vargs, **kwargs)`




#### `specify(*vargs, **kwargs)`






### `class Report()` 




#### `__init__(raw, query)`




#### `append(raw, query)`






### `function all(*values)` 




### `function any(*values)` 




### `function condition(value)` 




### `function copy(x)` 

Shallow copy operation on arbitrary Python objects. 
See the module's __doc__ string for more info.


### `function followed_by(*values)` 




### `function immediately_followed_by(*values)` 




### `function sequence(value)` 




