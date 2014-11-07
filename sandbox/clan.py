import json
import yaml
import googleanalytics as ga
blueprint = yaml.load(open('../examples/query.yml'))
profile = ga.blueprint.authenticate(blueprint)

if __name__ == '__main__':
    profile = ga.blueprint.authenticate(blueprint)
    queries = ga.blueprint.parse(blueprint, profile)

    reports = []
    for query in queries:
        report = query.execute()
        reports.append({
            'query': query.raw, 
            'results': report.serialize(), 
        })

    print json.dumps(reports, indent=2)
