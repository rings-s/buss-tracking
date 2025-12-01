/**
 * Web NFC API TypeScript Definitions (Latest 2025 Spec)
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Web_NFC_API
 * @see https://w3c.github.io/web-nfc/
 *
 * Browser Support: Chrome/Edge 89+ (Android only)
 * Note: Not available on iOS/desktop platforms
 */

// =============================================================================
// NDEF Record Types
// =============================================================================

/**
 * Standard NDEF record types
 */
type NDEFRecordType =
	| 'empty'
	| 'text'
	| 'url'
	| 'smart-poster'
	| 'absolute-url'
	| 'mime'
	| 'unknown'
	| string; // Allow external type names

/**
 * NDEF Record data - strongly typed based on record type
 */
type NDEFRecordData =
	| string // For text, url, absolute-url
	| ArrayBuffer // For binary data
	| DataView
	| Blob
	| object; // For structured data

// =============================================================================
// NDEF Message & Records
// =============================================================================

/**
 * Represents an NDEF message read from or written to an NFC tag
 */
interface NDEFMessage {
	/**
	 * Array of NDEF records contained in this message
	 */
	readonly records: readonly NDEFRecord[];
}

/**
 * Represents a single NDEF record
 */
interface NDEFRecord {
	/**
	 * Type of the NDEF record (e.g., 'text', 'url', 'mime')
	 */
	readonly recordType: NDEFRecordType;

	/**
	 * MIME type of the payload (for 'mime' record type)
	 */
	readonly mediaType?: string;

	/**
	 * Unique identifier for the record
	 */
	readonly id?: string;

	/**
	 * Record payload data
	 */
	readonly data?: DataView;

	/**
	 * Encoding for text records (e.g., 'utf-8')
	 */
	readonly encoding?: string;

	/**
	 * Language code for text records (e.g., 'en', 'ar')
	 */
	readonly lang?: string;

	/**
	 * Convert record data to JSON object
	 */
	toRecords?(): NDEFRecord[];
}

// =============================================================================
// NDEF Reading
// =============================================================================

/**
 * Event fired when an NFC tag is read
 */
interface NDEFReadingEvent extends Event {
	/**
	 * Serial number of the NFC tag (unique identifier)
	 */
	readonly serialNumber: string;

	/**
	 * NDEF message read from the tag
	 */
	readonly message: NDEFMessage;
}

/**
 * Options for NFC scanning
 */
interface NDEFScanOptions {
	/**
	 * AbortSignal to cancel the scan operation
	 */
	signal?: AbortSignal;
}

// =============================================================================
// NDEF Writing
// =============================================================================

/**
 * Initialization object for creating NDEF messages
 */
interface NDEFMessageInit {
	/**
	 * Array of record initializers
	 */
	records: NDEFRecordInit[];
}

/**
 * Initialization object for creating NDEF records
 */
interface NDEFRecordInit {
	/**
	 * Type of the NDEF record
	 */
	recordType: NDEFRecordType;

	/**
	 * MIME type (required for 'mime' record type)
	 */
	mediaType?: string;

	/**
	 * Optional record identifier
	 */
	id?: string;

	/**
	 * Text encoding (for 'text' records)
	 */
	encoding?: string;

	/**
	 * Language code (for 'text' records)
	 */
	lang?: string;

	/**
	 * Record payload data
	 */
	data?: NDEFRecordData;
}

/**
 * Options for writing to NFC tags
 */
interface NDEFWriteOptions {
	/**
	 * Whether to overwrite existing data on the tag
	 * @default true
	 */
	overwrite?: boolean;

	/**
	 * AbortSignal to cancel the write operation
	 */
	signal?: AbortSignal;
}

// =============================================================================
// NDEFReader API
// =============================================================================

/**
 * Main interface for reading and writing NFC tags
 *
 * @example
 * ```ts
 * const reader = new NDEFReader();
 * await reader.scan();
 *
 * reader.addEventListener('reading', ({ serialNumber, message }) => {
 *   console.log(`Tag ${serialNumber} contains ${message.records.length} records`);
 * });
 * ```
 */
interface NDEFReader extends EventTarget {
	/**
	 * Start scanning for NFC tags
	 *
	 * @param options - Scan options including abort signal
	 * @throws {DOMException} If permission is denied or NFC is unavailable
	 * @throws {NotSupportedError} If Web NFC is not supported
	 */
	scan(options?: NDEFScanOptions): Promise<void>;

	/**
	 * Write data to an NFC tag
	 *
	 * @param message - String, ArrayBuffer, or structured NDEF message
	 * @param options - Write options including overwrite and abort signal
	 * @throws {DOMException} If write fails or permission is denied
	 */
	write(
		message: string | ArrayBuffer | NDEFMessageInit,
		options?: NDEFWriteOptions
	): Promise<void>;

	/**
	 * Event fired when an NFC tag is successfully read
	 */
	addEventListener(
		type: 'reading',
		listener: (this: NDEFReader, ev: NDEFReadingEvent) => void,
		options?: boolean | AddEventListenerOptions
	): void;

	/**
	 * Event fired when an error occurs during reading
	 */
	addEventListener(
		type: 'readingerror',
		listener: (this: NDEFReader, ev: Event) => void,
		options?: boolean | AddEventListenerOptions
	): void;

	/**
	 * Generic event listener
	 */
	addEventListener(
		type: string,
		listener: EventListenerOrEventListenerObject,
		options?: boolean | AddEventListenerOptions
	): void;

	/**
	 * Remove event listener
	 */
	removeEventListener(
		type: string,
		listener: EventListenerOrEventListenerObject,
		options?: boolean | EventListenerOptions
	): void;

	/**
	 * Event handler for reading events
	 */
	onreading: ((this: NDEFReader, ev: NDEFReadingEvent) => void) | null;

	/**
	 * Event handler for reading errors
	 */
	onreadingerror: ((this: NDEFReader, ev: Event) => void) | null;
}

/**
 * NDEFReader constructor
 */
declare var NDEFReader: {
	prototype: NDEFReader;
	new (): NDEFReader;
};
