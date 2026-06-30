"use client";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useMemo, useRef } from "react";
import { STATUS_COLORS, statusLabel } from "@/lib/constants";
import type { Account } from "@/lib/types";

const OSM_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap contributors",
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

// Build a maplibre "match" expression: status -> color.
const COLOR_MATCH = [
  "match",
  ["get", "status"],
  ...Object.entries(STATUS_COLORS).flat(),
  "#000000",
] as unknown as maplibregl.ExpressionSpecification;

function toGeoJSON(accounts: Account[]): GeoJSON.FeatureCollection {
  return {
    type: "FeatureCollection",
    features: accounts
      .filter((a) => a.lat != null && a.lng != null)
      .map((a) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [a.lng as number, a.lat as number] },
        properties: { id: a.id, name: a.name, status: a.status },
      })),
  };
}

function fitToData(map: maplibregl.Map, fc: GeoJSON.FeatureCollection) {
  const coords = fc.features.map(
    (f) => (f.geometry as GeoJSON.Point).coordinates as [number, number],
  );
  if (coords.length === 0) return;
  if (coords.length === 1) {
    map.setCenter(coords[0]);
    map.setZoom(12);
    return;
  }
  const b = new maplibregl.LngLatBounds(coords[0], coords[0]);
  coords.forEach((c) => b.extend(c));
  map.fitBounds(b, { padding: 48, maxZoom: 13, duration: 0 });
}

export function AccountMap({ accounts }: { accounts: Account[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const fc = useMemo(() => toGeoJSON(accounts), [accounts]);

  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: OSM_STYLE,
      center: [-40, 20],
      zoom: 1.2,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl(), "top-right");

    map.on("load", () => {
      map.addSource("accounts", {
        type: "geojson",
        data: fc,
        cluster: true,
        clusterRadius: 50,
      });
      map.addLayer({
        id: "clusters",
        type: "circle",
        source: "accounts",
        filter: ["has", "point_count"],
        paint: {
          "circle-color": "#111111",
          "circle-radius": ["step", ["get", "point_count"], 16, 10, 22, 50, 28],
        },
      });
      map.addLayer({
        id: "cluster-count",
        type: "symbol",
        source: "accounts",
        filter: ["has", "point_count"],
        layout: { "text-field": ["get", "point_count_abbreviated"], "text-size": 12 },
        paint: { "text-color": "#ffffff" },
      });
      map.addLayer({
        id: "unclustered-point",
        type: "circle",
        source: "accounts",
        filter: ["!", ["has", "point_count"]],
        paint: {
          "circle-color": COLOR_MATCH,
          "circle-radius": 7,
          "circle-stroke-width": 1.5,
          "circle-stroke-color": "#ffffff",
        },
      });

      map.on("click", "clusters", (e) => {
        const f = map.queryRenderedFeatures(e.point, { layers: ["clusters"] })[0];
        const clusterId = f.properties?.cluster_id;
        const src = map.getSource("accounts") as maplibregl.GeoJSONSource;
        src.getClusterExpansionZoom(clusterId).then((zoom) => {
          map.easeTo({
            center: (f.geometry as GeoJSON.Point).coordinates as [number, number],
            zoom,
          });
        });
      });
      map.on("click", "unclustered-point", (e) => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as { id: string; name: string; status: string };
        const coords = (f.geometry as GeoJSON.Point).coordinates as [number, number];
        new maplibregl.Popup()
          .setLngLat(coords)
          .setHTML(
            `<div style="font-family:monospace;font-size:12px">
               <strong>${p.name}</strong><br/>${statusLabel(p.status)}<br/>
               <a href="/accounts/${p.id}">Open profile →</a>
             </div>`,
          )
          .addTo(map);
      });
      map.on("mouseenter", "clusters", () => (map.getCanvas().style.cursor = "pointer"));
      map.on("mouseleave", "clusters", () => (map.getCanvas().style.cursor = ""));
      map.on("mouseenter", "unclustered-point", () => (map.getCanvas().style.cursor = "pointer"));
      map.on("mouseleave", "unclustered-point", () => (map.getCanvas().style.cursor = ""));

      fitToData(map, fc);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // Init once; data updates handled below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;
    const src = map.getSource("accounts") as maplibregl.GeoJSONSource | undefined;
    if (src) {
      src.setData(fc);
      fitToData(map, fc);
    }
  }, [fc]);

  return <div ref={containerRef} className="h-[70vh] w-full rounded-lg border" />;
}
