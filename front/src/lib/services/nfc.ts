/**
 * Web NFC Service for reading NFC tags
 * Requires Chrome Android 89+ with HTTPS
 * Browser Support: Chrome Android, Samsung Internet, Opera Android
 * NOT supported on iOS
 */

export interface NFCReadResult {
	serialNumber: string;
	message?: string;
	records: NDEFRecord[];
}

export class NFCService {
	private reader: NDEFReader | null = null;
	private scanning = false;

	/**
	 * Check if Web NFC is supported in the current browser
	 */
	isSupported(): boolean {
		return 'NDEFReader' in window;
	}

	/**
	 * Check if currently scanning for NFC tags
	 */
	isScanning(): boolean {
		return this.scanning;
	}

	/**
	 * Request NFC permission and start scanning for tags
	 * @param onRead - Callback when NFC tag is read successfully
	 * @param onError - Callback when an error occurs
	 */
	async startScan(
		onRead: (result: NFCReadResult) => void,
		onError: (error: Error) => void
	): Promise<void> {
		if (!this.isSupported()) {
			throw new Error('Web NFC is not supported on this device or browser');
		}

		if (this.scanning) {
			throw new Error('Already scanning for NFC tags');
		}

		try {
			this.reader = new NDEFReader();
			await this.reader.scan();
			this.scanning = true;

			this.reader.addEventListener('reading', (event: NDEFReadingEvent) => {
				const result: NFCReadResult = {
					serialNumber: event.serialNumber,
					records: Array.from(event.message.records)
				};

				// Try to extract text message if available
				for (const record of event.message.records) {
					if (record.recordType === 'text' && record.data) {
						const textDecoder = new TextDecoder(record.encoding || 'utf-8');
						result.message = textDecoder.decode(record.data);
						break;
					}
				}

				onRead(result);
			});

			this.reader.addEventListener('readingerror', () => {
				onError(new Error('Cannot read data from the NFC tag. Try again.'));
			});
		} catch (error) {
			this.scanning = false;
			if (error instanceof Error) {
				// Handle specific error types
				if (error.name === 'NotAllowedError') {
					onError(new Error('NFC permission was denied. Please allow NFC access.'));
				} else if (error.name === 'NotSupportedError') {
					onError(new Error('NFC is not supported on this device.'));
				} else {
					onError(error);
				}
			} else {
				onError(new Error('Failed to start NFC scanning'));
			}
		}
	}

	/**
	 * Stop scanning for NFC tags
	 */
	stopScan(): void {
		this.scanning = false;
		this.reader = null;
	}

	/**
	 * Write data to NFC tag (optional - for future use)
	 * @param message - Text message to write to the tag
	 */
	async write(message: string): Promise<void> {
		if (!this.isSupported()) {
			throw new Error('Web NFC is not supported on this device or browser');
		}

		try {
			const writer = new NDEFReader();
			await writer.write(message);
		} catch (error) {
			if (error instanceof Error) {
				if (error.name === 'NotAllowedError') {
					throw new Error('NFC write permission was denied.');
				} else if (error.name === 'NetworkError') {
					throw new Error('NFC write failed. Make sure the tag is writable.');
				} else {
					throw error;
				}
			} else {
				throw new Error('Failed to write to NFC tag');
			}
		}
	}
}

// Export singleton instance
export const nfcService = new NFCService();
