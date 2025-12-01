<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { Map, Marker, Polyline, LatLngExpression } from 'leaflet';

	interface MapMarker {
		id: number | string;
		lat: number;
		lng: number;
		label?: string;
		color?: string;
		popup?: string;
		isVehicle?: boolean;
		isSelected?: boolean;
		heading?: number;
	}

	interface MapPath {
		coordinates: [number, number][];
		color?: string;
		weight?: number;
	}

	let {
		markers = [],
		paths = [],
		center = [0, 0] as [number, number],
		zoom = 13,
		height = '400px',
		showUserLocation = false,
		onMarkerClick = undefined as ((marker: MapMarker) => void) | undefined
	}: {
		markers?: MapMarker[];
		paths?: MapPath[];
		center?: [number, number];
		zoom?: number;
		height?: string;
		showUserLocation?: boolean;
		onMarkerClick?: (marker: MapMarker) => void;
	} = $props();

	let mapContainer: HTMLDivElement;
	let map: Map | null = $state(null);
	let leafletMarkers: Marker[] = [];
	let leafletPaths: Polyline[] = [];
	let userMarker: Marker | null = null;
	let L: typeof import('leaflet') | null = $state(null);

	onMount(async () => {
		// Dynamic import for SSR compatibility
		const leaflet = await import('leaflet');

		// Import CSS
		await import('leaflet/dist/leaflet.css');

		// Fix default marker icons
		delete (leaflet.Icon.Default.prototype as any)._getIconUrl;
		leaflet.Icon.Default.mergeOptions({
			iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
			iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
			shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
		});

		// Initialize map
		const mapInstance = leaflet.map(mapContainer).setView(center, zoom);

		// Add tile layer (OpenStreetMap)
		leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(mapInstance);

		// Set state to trigger effects
		L = leaflet;
		map = mapInstance;

		// Show user location if requested
		if (showUserLocation) {
			trackUserLocation();
		}
	});

	onDestroy(() => {
		if (map) {
			map.remove();
			map = null;
		}
	});

	function createColoredIcon(color: string) {
		if (!L) return undefined;

		return L.divIcon({
			className: 'custom-marker',
			html: `<div style="
				background-color: ${color};
				width: 24px;
				height: 24px;
				border-radius: 50%;
				border: 3px solid white;
				box-shadow: 0 2px 5px rgba(0,0,0,0.3);
			"></div>`,
			iconSize: [24, 24],
			iconAnchor: [12, 12],
			popupAnchor: [0, -12]
		});
	}

	function createVehicleIcon(color: string, isSelected: boolean = false, heading: number = 0) {
		if (!L) return undefined;

		const size = isSelected ? 44 : 36;
		const pulseClass = isSelected ? 'vehicle-pulse' : '';

		return L.divIcon({
			className: 'vehicle-marker',
			html: `
				<div class="vehicle-icon-wrapper ${pulseClass}" style="width: ${size}px; height: ${size}px;">
					<div class="vehicle-icon" style="
						width: 100%;
						height: 100%;
						background: ${color};
						border-radius: 50% 50% 50% 0;
						transform: rotate(${heading - 45}deg);
						border: 3px solid white;
						box-shadow: 0 3px 10px rgba(0,0,0,0.4);
						display: flex;
						align-items: center;
						justify-content: center;
					">
						<svg
							viewBox="0 0 24 24"
							fill="white"
							style="width: 60%; height: 60%; transform: rotate(${45 - heading}deg);"
						>
							<path d="M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6H6V6h12v5z"/>
						</svg>
					</div>
				</div>
			`,
			iconSize: [size, size],
			iconAnchor: [size / 2, size / 2],
			popupAnchor: [0, -size / 2]
		});
	}

	function trackUserLocation() {
		if (!navigator.geolocation || !map || !L) return;

		navigator.geolocation.watchPosition(
			(position) => {
				const { latitude, longitude } = position.coords;

				if (userMarker) {
					userMarker.setLatLng([latitude, longitude]);
				} else {
					const icon = createColoredIcon('#10b981');
					if (icon) {
						userMarker = L!.marker([latitude, longitude], { icon })
							.addTo(map!)
							.bindPopup('Your Location');
					}
				}
			},
			(error) => {
				console.error('Geolocation error:', error);
			},
			{
				enableHighAccuracy: true,
				maximumAge: 10000,
				timeout: 5000
			}
		);
	}

	// Reactive effect for markers - explicitly read markers array to create dependency
	$effect(() => {
		if (!map || !L) return;

		// Read markers to establish dependency (access length and items)
		const currentMarkers = markers;
		const markerCount = currentMarkers.length;

		// Remove existing markers
		leafletMarkers.forEach(m => m.remove());
		leafletMarkers = [];

		// Add new markers
		currentMarkers.forEach(marker => {
			let icon;
			if (marker.isVehicle) {
				icon = createVehicleIcon(
					marker.color || '#3b82f6',
					marker.isSelected || false,
					marker.heading || 0
				);
			} else {
				icon = marker.color ? createColoredIcon(marker.color) : new L!.Icon.Default();
			}

			const leafletMarker = L!.marker([marker.lat, marker.lng], { icon: icon || undefined })
				.addTo(map!);

			if (marker.popup) {
				leafletMarker.bindPopup(marker.popup);
			} else if (marker.label) {
				leafletMarker.bindPopup(`<strong>${marker.label}</strong>`);
			}

			if (onMarkerClick) {
				leafletMarker.on('click', () => onMarkerClick(marker));
			}

			leafletMarkers.push(leafletMarker);
		});

		// Only fit bounds on initial load (when no marker is selected)
		const hasSelectedMarker = currentMarkers.some(m => m.isSelected);
		if (markerCount > 0 && !hasSelectedMarker) {
			const bounds = L.latLngBounds(currentMarkers.map(m => [m.lat, m.lng] as LatLngExpression));
			map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
		}
	});

	// Reactive effect for paths - explicitly read paths array to create dependency
	$effect(() => {
		if (!map || !L) return;

		// Read paths to establish dependency
		const currentPaths = paths;
		const pathCount = currentPaths.length;

		// Remove existing paths
		leafletPaths.forEach(p => p.remove());
		leafletPaths = [];

		// Add new paths
		currentPaths.forEach(path => {
			// Ensure coordinates are valid
			if (path.coordinates && path.coordinates.length > 0) {
				const polyline = L!.polyline(path.coordinates, {
					color: path.color || '#3b82f6',
					weight: path.weight || 4,
					opacity: 0.9
				}).addTo(map!);

				leafletPaths.push(polyline);
			}
		});
	});

	// Public methods
	export function setView(lat: number, lng: number, newZoom?: number) {
		if (map) {
			map.setView([lat, lng], newZoom || zoom);
		}
	}

	export function flyTo(lat: number, lng: number, newZoom?: number) {
		if (map) {
			map.flyTo([lat, lng], newZoom || zoom, {
				duration: 1,
				easeLinearity: 0.5
			});
		}
	}

	export function fitBounds(bounds: [[number, number], [number, number]]) {
		if (map && L) {
			map.fitBounds(L.latLngBounds(bounds));
		}
	}

	export function fitBoundsWithPadding(coords: [number, number][], padding: number = 50, maxZoom: number = 16) {
		if (map && L && coords.length > 0) {
			const bounds = L.latLngBounds(coords.map(c => [c[0], c[1]] as LatLngExpression));
			map.fitBounds(bounds, { padding: [padding, padding], maxZoom });
		}
	}

	export function getMap() {
		return map;
	}
</script>

<div bind:this={mapContainer} class="leaflet-map" style="height: {height}; width: 100%;"></div>

<style>
	.leaflet-map {
		border-radius: 8px;
		z-index: 0;
	}

	:global(.custom-marker) {
		background: transparent !important;
		border: none !important;
	}

	:global(.vehicle-marker) {
		background: transparent !important;
		border: none !important;
	}

	:global(.vehicle-icon-wrapper) {
		position: relative;
	}

	:global(.vehicle-pulse) {
		animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	:global(.vehicle-pulse::before) {
		content: '';
		position: absolute;
		inset: -8px;
		border-radius: 50%;
		background: rgba(59, 130, 246, 0.3);
		animation: pulse-expand 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	@keyframes pulse-ring {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.8;
		}
	}

	@keyframes pulse-expand {
		0% {
			transform: scale(0.8);
			opacity: 0.8;
		}
		50% {
			transform: scale(1.2);
			opacity: 0;
		}
		100% {
			transform: scale(0.8);
			opacity: 0;
		}
	}
</style>
