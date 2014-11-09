# None

None


### `class Account()`

An account is usually but not always associated with a single  website. It will often contain multiple web properties  (different parts of your website that you've configured Google Analytics to analyze separately, or simply the default web property that every website has in Google Analytics),  which in turn will have one or more profiles. 
You should navigate to a profile to run queries. 
```python import googleanalytics as ga accounts = ga.authenticate() profile = accounts['debrouwere.org'].webproperties['UA-12933299-1'].profiles['debrouwere.org'] report = profile.query('pageviews').range('2014-10-01', '2014-10-31').execute() print report['pageviews'] ```


#### `__init__(raw, service)`




#### ``




#### ``




#### ``




#### ``




#### ``




#### ``




#### ``






### `class Profile()`

A profile is a particular analytics configuration of a web property. Each profile belongs to a web property and an account. As all  queries using the Google Analytics API run against a particular profile, queries can only be created from a `Profile` object. 
```python profile.query('pageviews').range('2014-01-01', days=7).execute() ```


#### `__init__(raw, webproperty)`




#### `live(metrics=[], dimensions=[])`

Return a query for certain metrics and dimensions, using the live API. 
**Note:** this is a placeholder and not implemented yet.


#### `query(metrics=[], dimensions=[])`

Return a query for certain metrics and dimensions. 
```python # pageviews (metric) as a function of geographical region profile.query('pageviews', 'region') # pageviews as a function of browser profile.query(['pageviews'], ['browser']) ``` 
The returned query can then be further refined using  all methods available on the `CoreQuery` object, such as  `limit`, `sort`, `segment` and so on. 
Metrics and dimensions may be either strings (the column id or the human-readable column name) or Metric or Dimension  objects. 
Metrics and dimensions specified as a string are not case-sensitive. 
```python profile.query ``` 
If specifying only a single metric or dimension, you can  but are not required to wrap it in a list.




### `class WebProperty()`

A web property is a particular website you're tracking in Google Analytics. It has one or more profiles, and you will need to pick one from which to  launch your queries.


#### `__init__(raw, account)`




#### ``




#### `query(*vargs, **kwargs)`

A shortcut to the first profile of this webproperty.




