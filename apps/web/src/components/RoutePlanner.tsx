"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { format, type Dictionary } from "@/i18n";
import { ApiError, findRouteOrigins, getWalkingRoute } from "@/lib/api";
import type { GeoLocation, Place, RouteOrigin, WalkingRoute } from "@/lib/types";
import type { GeoJSONSource, Map as MapLibreMap, Marker } from "maplibre-gl";

const mapKey = process.env.NEXT_PUBLIC_MAPTILER_KEY;

export function RoutePlanner({ place, dict }: { place: Place; dict: Dictionary }) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const maplibreRef = useRef<typeof import("maplibre-gl") | null>(null);
  const originMarker = useRef<Marker | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [mapError, setMapError] = useState(false);
  const [address, setAddress] = useState("");
  const [origins, setOrigins] = useState<RouteOrigin[]>([]);
  const [startLabel, setStartLabel] = useState("");
  const [route, setRoute] = useState<WalkingRoute | null>(null);
  const [searching, setSearching] = useState(false);
  const [routing, setRouting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!mapKey || !mapContainer.current) return;
    let disposed = false;

    import("maplibre-gl").then((maplibre) => {
      if (disposed || !mapContainer.current) return;
      const workerUrl = new URL("maplibre-gl/dist/maplibre-gl-worker.mjs?maplibre-worker-asset", import.meta.url);
      const sharedUrl = new URL("maplibre-gl/dist/maplibre-gl-shared.mjs?maplibre-worker-asset", import.meta.url);
      if (workerUrl.origin !== sharedUrl.origin) throw new Error("MapLibre worker assets must share an origin");
      maplibre.setWorkerUrl(workerUrl.toString());
      maplibreRef.current = maplibre;
      const map = new maplibre.Map({
        container: mapContainer.current,
        style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${encodeURIComponent(mapKey)}`,
        center: [place.location.lng, place.location.lat],
        zoom: 14
      });
      map.addControl(new maplibre.NavigationControl({ showCompass: false }), "top-right");
      new maplibre.Marker({ color: "#0064b6" })
        .setLngLat([place.location.lng, place.location.lat])
        .addTo(map);
      map.on("load", () => setMapReady(true));
      map.on("error", () => setMapError(true));
      mapRef.current = map;
    }).catch(() => {
      if (!disposed) setMapError(true);
    });

    return () => {
      disposed = true;
      mapRef.current?.remove();
      mapRef.current = null;
      maplibreRef.current = null;
      originMarker.current = null;
    };
  }, [place.id, place.location.lat, place.location.lng]);

  useEffect(() => {
    const map = mapRef.current;
    const maplibre = maplibreRef.current;
    if (!mapReady || !map || !maplibre) return;

    const source = map.getSource("walking-route") as GeoJSONSource | undefined;
    originMarker.current?.remove();
    originMarker.current = null;
    if (!route) {
      source?.setData({ type: "FeatureCollection", features: [] });
      return;
    }

    const coordinates = route.geometry.coordinates;
    const data = { type: "Feature" as const, properties: {}, geometry: route.geometry };
    if (source) {
      source.setData(data);
    } else {
      map.addSource("walking-route", { type: "geojson", data });
      map.addLayer({
        id: "walking-route-line",
        type: "line",
        source: "walking-route",
        paint: { "line-color": "#b34025", "line-width": 5 }
      });
    }
    originMarker.current = new maplibre.Marker({ color: "#b34025" })
      .setLngLat(coordinates[0])
      .addTo(map);
    const bounds = new maplibre.LngLatBounds(coordinates[0], coordinates[0]);
    coordinates.forEach((point) => bounds.extend(point));
    map.fitBounds(bounds, { padding: 55, maxZoom: 16 });
  }, [route, mapReady]);

  async function calculateRoute(start: GeoLocation, label: string) {
    setError("");
    setRoute(null);
    setOrigins([]);
    setStartLabel(label);
    setRouting(true);
    try {
      setRoute(await getWalkingRoute(place.id, start));
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 404) setError(dict.route.noRoute);
      else if (cause instanceof ApiError && cause.status === 503) setError(dict.route.notConfigured);
      else setError(dict.route.routeError);
    } finally {
      setRouting(false);
    }
  }

  function useCurrentLocation() {
    if (!navigator.geolocation) {
      setError(dict.route.locationDenied);
      return;
    }
    setError("");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        void calculateRoute(
          { lat: position.coords.latitude, lng: position.coords.longitude },
          dict.route.currentLocation
        );
      },
      () => setError(dict.route.locationDenied),
      { timeout: 10000, maximumAge: 60000 }
    );
  }

  async function searchAddress(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (address.trim().length < 3) return;
    setError("");
    setOrigins([]);
    setSearching(true);
    try {
      const results = await findRouteOrigins(address.trim());
      setOrigins(results);
      if (!results.length) setError(dict.route.noAddresses);
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 503) setError(dict.route.notConfigured);
      else setError(dict.route.addressError);
    } finally {
      setSearching(false);
    }
  }

  return (
    <section id="route" className="mt-8 scroll-mt-6" aria-labelledby="route-heading">
      <h2 id="route-heading" className="kr-card-blue px-4 py-3 text-xl font-bold">
        {dict.route.heading}
      </h2>
      <div className="border border-t-0 border-[var(--color-rule)]">
        <div className="grid gap-5 p-4 md:grid-cols-[minmax(16rem,20rem)_minmax(0,1fr)] md:p-5">
          <div className="space-y-4">
            <button type="button" onClick={useCurrentLocation} disabled={routing || searching} className="kr-btn">
              {dict.route.currentLocation}
            </button>
            <form onSubmit={(event) => void searchAddress(event)} className="space-y-2">
              <label htmlFor="route-origin" className="block font-bold">{dict.route.startAddress}</label>
              <input
                id="route-origin"
                type="search"
                value={address}
                minLength={3}
                required
                onChange={(event) => { setAddress(event.target.value); setOrigins([]); }}
                placeholder={dict.route.addressPlaceholder}
                className="w-full min-w-0 border-2 border-[var(--color-rule)] px-3 py-2"
              />
              <button type="submit" disabled={searching || routing} className="kr-btn">
                {searching ? dict.route.searchPending : dict.route.searchAddress}
              </button>
            </form>
            {origins.length > 0 && (
              <div>
                <p className="font-bold">{dict.route.addressResults}</p>
                <ul className="mt-2 border border-[var(--color-rule)]">
                  {origins.map((origin, index) => (
                    <li key={`${origin.label}-${index}`} className="border-b border-[var(--color-rule)] last:border-0">
                      <button
                        type="button"
                        className="w-full px-3 py-2 text-left underline hover:bg-[var(--color-krakow-tint)]"
                        disabled={routing}
                        onClick={() => void calculateRoute(origin.location, origin.label)}
                      >
                        {origin.label}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div role="status" aria-live="polite">
              {routing && <p>{dict.route.calculating}</p>}
              {error && <p className="text-[#9a331d]">{error}</p>}
              {route && (
                <div className="space-y-1">
                  <p className="font-bold">{format(dict.route.summary, {
                    distance: (route.distance_m / 1000).toLocaleString(dict.localeTag, { maximumFractionDigits: 1 }),
                    minutes: Math.ceil(route.duration_s / 60)
                  })}</p>
                  <p className="text-sm">{startLabel} → {place.name}</p>
                </div>
              )}
            </div>
          </div>
          <div className="min-w-0">
            {mapKey ? (
              <div
                ref={mapContainer}
                role="region"
                aria-label={format(dict.route.mapLabel, { place: place.name })}
                className="h-96 min-h-72 w-full border border-[var(--color-rule)]"
              />
            ) : null}
            {(mapError || !mapKey) && <p className="text-sm text-[var(--color-muted)]">{dict.route.mapUnavailable}</p>}
          </div>
        </div>
      </div>
    </section>
  );
}
