import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.xml.bind.DatatypeConverter;
import javax.crypto.spec.SecretKeySpec;

import java.security.MessageDigest;
import java.util.Arrays;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class AES {

    public static void main(String[] args) throws Exception {
        String plainText = "Hello World";
        String keyText ="123";
        SecretKey secKey = getSecretEncryptionKey(keyText);
        System.out.println("secKey:" + secKey);

        byte[] cipherText = encryptText(plainText, secKey);
        String decryptedText = decryptText(cipherText, secKey);

        System.out.println("Original Text:>>>> " + plainText);
        System.out.println("AES Key (Hex Form):>>>> "+bytesToHex(secKey.getEncoded()));
        System.out.println("Encrypted Text (Hex Form):>>>> "+bytesToHex(cipherText));
        System.out.println("Descrypted Text:>>>> "+decryptedText);
    }

  public static SecretKey getSecretEncryptionKey(String keyText) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(getKey(keyText), "AES");
        return keySpec;
    }

  public static byte[] getKey(String keyStr) {
        byte[] key = null;
        try {
            key = (keyStr).getBytes("UTF-8");
            MessageDigest sha = MessageDigest.getInstance("SHA-1");
            key = sha.digest(key);
            System.out.println("SHA-1 key" + key);  
            key = Arrays.copyOf(key, 16);
            System.out.println("copyOf SHA-1 16 key" + key);        
        } catch (Exception e) {
            e.printStackTrace();
        }

     System.out.println("getKey" + key);
        return key;
    }

    public static byte[] encryptText(String plainText,SecretKey secKey) throws Exception{
        // AES defaults to AES/ECB/PKCS5Padding in Java 7
        Cipher aesCipher = Cipher.getInstance("AES");
        aesCipher.init(Cipher.ENCRYPT_MODE, secKey);
        byte[] byteCipherText = aesCipher.doFinal(plainText.getBytes());
        return byteCipherText;
    }

    public static String decryptText(byte[] byteCipherText, SecretKey secKey) throws Exception {
        // AES defaults to AES/ECB/PKCS5Padding in Java 7
        Cipher aesCipher = Cipher.getInstance("AES");
        aesCipher.init(Cipher.DECRYPT_MODE, secKey);
        byte[] bytePlainText = aesCipher.doFinal(byteCipherText);
        return new String(bytePlainText);
    }

    private static String  bytesToHex(byte[] hash) {
        return DatatypeConverter.printHexBinary(hash);
    }
}