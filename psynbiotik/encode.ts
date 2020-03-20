import * as CryptoJs from "crypto-js"

export class AESEncryption {
    static encrypt(payload: string, secretKey: string): string {
        var hash = CryptoJs.SHA1(CryptoJs.enc.Utf8.parse(secretKey));
        var key = CryptoJs.enc.Hex.parse(hash.toString(CryptoJs.enc.Hex).substr(0, 32));
        
        const encrypted = CryptoJs.AES.encrypt(payload, key, {
            mode:     CryptoJs.mode.ECB,
            padding:  CryptoJs.pad.Pkcs7
        });
        const words = CryptoJs.enc.Base64.parse(encrypted.toString())

        return CryptoJs.enc.Hex.stringify(words).toUpperCase();
    }

    static decrypt(payload: string, secretKey: string): string {
        const words = CryptoJs.enc.Hex.parse(payload)
        payload = CryptoJs.enc.Base64.stringify(words);
        var hash = CryptoJs.SHA1(CryptoJs.enc.Utf8.parse(secretKey));
        var key = CryptoJs.enc.Hex.parse(hash.toString(CryptoJs.enc.Hex).substr(0, 32));
        
        const decrypted = CryptoJs.AES.decrypt(payload, key, {
            mode:     CryptoJs.mode.ECB,
            padding:  CryptoJs.pad.Pkcs7
        });
        return decrypted.toString(CryptoJs.enc.Utf8);

        // const s: string = CryptoJs.SHA256(secretKey).toString()//.substr(0, 8);
        // console.log("Decrypt Secret: ", s)
        // return CryptoJs.AES.decrypt(payload, secretKey, {
        //     keySize: 16,
        //     mode: CryptoJs.mode.CBC,
        //     padding: CryptoJs.pad.Pkcs7
        // }).toString(CryptoJs.enc.Utf8);
    }
}

const main = () => {
    // console.log(CryptoJs)
    console.log("Running Main")
    const data = AESEncryption.encrypt("Hello World", "123")
    console.log("Encode", data);
    console.log("Decode", AESEncryption.decrypt(data, "123"))
}
main();