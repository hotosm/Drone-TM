import { useEffect } from 'react';

export default function VectorLayerWithCluster({
  map,
  visibleOnMap,
  mapLoaded,
  sourceId,
  geojson,
}: any) {
  useEffect(() => {
    if (!map || !mapLoaded || !visibleOnMap || !sourceId) return;

    !map.getSource(sourceId) &&
      map.addSource(sourceId, {
        type: 'geojson',
        data: geojson,
        cluster: true,
        clusterMaxZoom: 14,
        clusterRadius: 40,
      });

    !map.getLayer('clusters') &&
      map.addLayer({
        id: 'clusters',
        type: 'circle',
        source: sourceId,
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': '#D73F3F',
          'circle-radius': 15,
        },
      });

    map.setGlyphs(
      'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
    );

    !map.getLayer('cluster-count') &&
      map.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: sourceId,
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-size': 12,
        },
        paint: {
          'text-color': '#fff',
        },
      });

    map.addLayer({
      id: 'unclustered-point',
      type: 'circle',
      source: sourceId,
      filter: ['!', ['has', 'point_count']],
      paint: {
        'circle-color': '#11b4da',
        'circle-radius': 6,
        'circle-stroke-width': 1,
        'circle-stroke-color': '#fff',
      },
      layout: {},
    });

    // inspect a cluster on click
    map.on('click', 'clusters', (e: any) => {
      const features = map.queryRenderedFeatures(e.point, {
        layers: ['clusters'],
      });
      const clusterId = features[0].properties.cluster_id;
      map
        .getSource(sourceId)
        .getClusterExpansionZoom(clusterId, (err: any, zoom: any) => {
          if (err) return;
          map.easeTo({
            center: features[0].geometry.coordinates,
            zoom,
          });
        });
    });

    map.on('mouseenter', 'clusters', () => {
      map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'clusters', () => {
      map.getCanvas().style.cursor = '';
    });

    map.on('mouseenter', 'unclustered-point', () => {
      map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'unclustered-point', () => {
      map.getCanvas().style.cursor = '';
    });

    return () => {
      if (sourceId) {
        if (map.getLayer(sourceId)) {
          map.removeLayer(sourceId);
        }
      }
    };
  }, [geojson, map, mapLoaded, sourceId, visibleOnMap]);

  return null;
}
