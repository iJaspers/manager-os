# Scout knowledge navigation experiment

A small optional topic map inspired by the idea of navigable knowledge maps in
[Understand Anything](https://github.com/Egonex-AI/Understand-Anything/tree/5338971c07a560c5fb6b26d85ad348b01315e2da). No
upstream code, graph service, indexing, or dependency is used. It complements
Scout's existing source-context view, which answers a different question:
what evidence participated in this handoff?

```sh
python3 -B experiments/wit-scout-explain/knowledge-map/knowledge_map.py "source coverage"
python3 -B experiments/wit-scout-explain/knowledge-map/knowledge_map.py "scout"
```

The first resolves one documented source pointer marked experimental. The
second returns both choices as AMBIGUOUS without picking a default. Unlisted
topics, including partial aliases, stay UNKNOWN. Paths are relative to the repo
root, not opened by the tool, and the map is curated rather than generated.
ROUTED means one declared pointer exists, not that a source was read or verified.
Update the existing source docs, not this map, for changes to release status.
