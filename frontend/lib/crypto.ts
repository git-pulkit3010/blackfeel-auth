export async function sha256(message: string): Promise<Uint8Array> {
    const encoder = new TextEncoder();
    const data = encoder.encode(message);

    if (typeof crypto !== 'undefined' && crypto.subtle) {
        const hash = await crypto.subtle.digest('SHA-256', data);
        return new Uint8Array(hash);
    }

    // Fallback for insecure contexts (only for development)
    // This uses a simple JS implementation of SHA-256
    // Note: For production, always use HTTPS to enable crypto.subtle
    return sha256JS(data);
}

function sha256JS(data: Uint8Array): Uint8Array {
    // Minimal SHA-256 implementation
    const K = [
        0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
        0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
        0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
        0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
        0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
        0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
        0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
        0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2
    ];

    function rotr(n: number, x: number) { return (x >>> n) | (x << (32 - n)); }
    function ch(x: number, y: number, z: number) { return (x & y) ^ (~x & z); }
    function maj(x: number, y: number, z: number) { return (x & y) ^ (x & z) ^ (y & z); }
    function sigma0(x: number) { return rotr(2, x) ^ rotr(13, x) ^ rotr(22, x); }
    function sigma1(x: number) { return rotr(6, x) ^ rotr(11, x) ^ rotr(25, x); }
    function gamma0(x: number) { return rotr(7, x) ^ rotr(18, x) ^ (x >>> 3); }
    function gamma1(x: number) { return rotr(17, x) ^ rotr(19, x) ^ (x >>> 10); }

    let H = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19];

    const totalLength = data.length * 8;
    const padding = [0x80];
    while ((data.length + padding.length + 8) % 64 !== 0) {
        padding.push(0);
    }

    const lenBytes = new Uint8Array(8);
    // Only handling 32-bit length for simplicity in this fallback
    lenBytes[4] = (totalLength >>> 24) & 0xff;
    lenBytes[5] = (totalLength >>> 16) & 0xff;
    lenBytes[6] = (totalLength >>> 8) & 0xff;
    lenBytes[7] = totalLength & 0xff;

    const paddedData = new Uint8Array(data.length + padding.length + 8);
    paddedData.set(data);
    paddedData.set(padding, data.length);
    paddedData.set(lenBytes, data.length + padding.length);

    for (let i = 0; i < paddedData.length; i += 64) {
        const chunk = paddedData.slice(i, i + 64);
        const W = new Uint32Array(64);

        for (let j = 0; j < 16; j++) {
            W[j] = (chunk[j * 4] << 24) | (chunk[j * 4 + 1] << 16) | (chunk[j * 4 + 2] << 8) | chunk[j * 4 + 3];
        }

        for (let j = 16; j < 64; j++) {
            W[j] = (gamma1(W[j - 2]) + W[j - 7] + gamma0(W[j - 15]) + W[j - 16]) | 0;
        }

        let [a, b, c, d, e, f, g, h] = H;

        for (let j = 0; j < 64; j++) {
            const T1 = (h + sigma1(e) + ch(e, f, g) + K[j] + W[j]) | 0;
            const T2 = (sigma0(a) + maj(a, b, c)) | 0;
            h = g; g = f; f = e; e = (d + T1) | 0; d = c; c = b; b = a; a = (T1 + T2) | 0;
        }

        H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
        H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
    }

    const result = new Uint8Array(32);
    for (let i = 0; i < 8; i++) {
        result[i * 4] = (H[i] >>> 24) & 0xff;
        result[i * 4 + 1] = (H[i] >>> 16) & 0xff;
        result[i * 4 + 2] = (H[i] >>> 8) & 0xff;
        result[i * 4 + 3] = H[i] & 0xff;
    }
    return result;
}
