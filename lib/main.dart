import 'dart:convert';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;

// =========================================================
// 1. GLOBAL SESSION & THEME
// =========================================================
class JurySession {
  static String? activeUserPhone;
  static int userAge = 0;
  static double hdfcBalance = 50000.00;
  static double dcbBalance = 2500.00;
  
  // IMPORTANT: Use 10.0.2.2 for Android Emulator
  // Use your Laptop's Local IP (e.g. 192.168.1.XX) for physical devices
  static const String serverIp = "10.0.2.2"; 

  static void reset() {
    activeUserPhone = null;
    userAge = 0;
    hdfcBalance = 50000.00;
    dcbBalance = 2500.00;
  }
  
}

const Color kBrandBlue = Color(0xFF2E3192);
const Color kBrandLightBlue = Color(0xFF1BFFFF);
const Color kBgColor = Color(0xFFF5F7FA);
const Color kWhite = Colors.white;
const Color kSuccess = Color(0xFF00C853);
const Color kDanger = Color(0xFFD50000);

void main() {
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: AppSplashScreen(),
  ));
}

// =========================================================
// 2. SPLASH & LOGIN
// =========================================================
class AppSplashScreen extends StatefulWidget {
  const AppSplashScreen({super.key});
  @override
  State<AppSplashScreen> createState() => _AppSplashScreenState();
}

class _AppSplashScreenState extends State<AppSplashScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(seconds: 2), () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const LoginScreen())));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(gradient: LinearGradient(colors: [kBrandBlue, Color(0xFF1B2845)])),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.shield_rounded, size: 80, color: kBrandLightBlue),
            SizedBox(height: 20),
            Text("UPIRAKSHAK SAFEGUARD", style: TextStyle(color: kWhite, fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 2)),
          ],
        ),
      ),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _phone = TextEditingController();
  final TextEditingController _age = TextEditingController();

  Future<void> _handleLogin() async {
    if (_phone.text.length != 10) { _showError("Phone must be 10 digits"); return; }
    if (_age.text.isEmpty) { _showError("Please enter your age"); return; }

    JurySession.activeUserPhone = _phone.text;
    JurySession.userAge = int.tryParse(_age.text) ?? 0;

    // Sync to PostgreSQL
    try {
      await http.post(
        Uri.parse("http://${JurySession.serverIp}:8000/feedback"), // Sync via feedback or specific user endpoint
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "tx": {"phone": JurySession.activeUserPhone, "age": JurySession.userAge},
          "is_fraud": 0
        }),
      );
    } catch (e) { debugPrint("PostgreSQL Sync failed: $e"); }

    if (!mounted) return;
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const SecurityDashboard()));
  }

  void _showError(String m) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(m)));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kWhite,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(30.0),
        child: Column(
          children: [
            const SizedBox(height: 80),
            const Text("User Login", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: kBrandBlue)),
            const SizedBox(height: 40),
            TextField(
              controller: _phone,
              keyboardType: TextInputType.phone,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly, LengthLimitingTextInputFormatter(10)],
              decoration: InputDecoration(prefixIcon: const Icon(Icons.phone), hintText: "Phone Number", border: OutlineInputBorder(borderRadius: BorderRadius.circular(15))),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: _age,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(prefixIcon: const Icon(Icons.cake), hintText: "Age", border: OutlineInputBorder(borderRadius: BorderRadius.circular(15))),
            ),
            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity, height: 55,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: kBrandBlue, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))),
                onPressed: _handleLogin,
                child: const Text("ACCESS DASHBOARD", style: TextStyle(color: kWhite, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// =========================================================
// 3. SECURITY DASHBOARD
// =========================================================
class SecurityDashboard extends StatefulWidget {
  const SecurityDashboard({super.key});
  @override
  State<SecurityDashboard> createState() => _SecurityDashboardState();
}

class _SecurityDashboardState extends State<SecurityDashboard> {
  String _loc = "Detecting GPS...";
  StreamSubscription<Position>? _positionStream;
  bool _isMocked = false;
  
  @override
  void initState() {
    super.initState();
    _startLiveLocationSync();
  }

  void _startLiveLocationSync() async {
    await [Permission.location].request();
    const locationSettings = LocationSettings(accuracy: LocationAccuracy.high, distanceFilter: 10);

    _positionStream = Geolocator.getPositionStream(locationSettings: locationSettings).listen((Position position) {
      setState(() {
        _isMocked = position.isMocked;
        _loc = _isMocked ? "⚠️ MOCK LOCATION DETECTED" : "Lat: ${position.latitude.toStringAsFixed(4)}, Lon: ${position.longitude.toStringAsFixed(4)}";
      });
    });
  }

  @override
  void dispose() { _positionStream?.cancel(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBgColor,
      body: SingleChildScrollView(
        child: Column(
          children: [
            _buildHeader(),
            const SizedBox(height: 20),
            _buildBalanceCard(),
            _buildActionsGrid(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.only(top: 60, left: 20, right: 20, bottom: 40),
      decoration: const BoxDecoration(gradient: LinearGradient(colors: [kBrandBlue, Color(0xFF1B2845)]), borderRadius: BorderRadius.vertical(bottom: Radius.circular(30))),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text("ID: ${JurySession.activeUserPhone}", style: const TextStyle(color: kWhite, fontWeight: FontWeight.bold)),
              IconButton(icon: const Icon(Icons.logout, color: Colors.red), onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const LoginScreen()))),
            ],
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: Colors.white10, borderRadius: BorderRadius.circular(15)),
            child: Row(children: [const Icon(Icons.location_on, color: kBrandLightBlue), const SizedBox(width: 10), Text(_loc, style: const TextStyle(color: kWhite, fontSize: 12))]),
          )
        ],
      ),
    );
  }

  Widget _buildBalanceCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: kWhite, borderRadius: BorderRadius.circular(20), boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10)]),
      child: Column(children: [
          _row("HDFC Bank Balance", "₹${JurySession.hdfcBalance}"),
          const Divider(height: 30),
          _row("DCB Bank Balance", "₹${JurySession.dcbBalance}"),
      ]),
    );
  }

  Widget _row(String t, String v) => Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text(t), Text(v, style: const TextStyle(fontWeight: FontWeight.bold))]);

  Widget _buildActionsGrid() {
    return GridView.count(
      shrinkWrap: true, padding: const EdgeInsets.all(20), crossAxisCount: 2, crossAxisSpacing: 15, mainAxisSpacing: 15,
      children: [
        _btn(Icons.qr_code_scanner, "SCAN QR", kBrandBlue, () => Navigator.push(context, MaterialPageRoute(builder: (context) => const QRScannerPage()))),
        _btn(Icons.warning_amber_rounded, "PHISHING TEST", Colors.orange, () => Navigator.push(context, MaterialPageRoute(builder: (context) => BankSelectionPage(rawData: "upi://pay?pa=malicious@upi&pn=FAKE%20REWARD", riskFlag: true, mockLoc: _isMocked)))),
      ],
    );
  }

  Widget _btn(IconData i, String l, Color c, VoidCallback t) => InkWell(
    onTap: t,
    child: Container(decoration: BoxDecoration(color: kWhite, borderRadius: BorderRadius.circular(20)), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(i, size: 40, color: c), const SizedBox(height: 10), Text(l, style: TextStyle(fontWeight: FontWeight.bold, color: c))])),
  );
}

// =========================================================
// 4. SCANNER & SELECTION
// =========================================================
class QRScannerPage extends StatelessWidget {
  const QRScannerPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: MobileScanner(onDetect: (capture) {
        final barcode = capture.barcodes.first;
        if (barcode.rawValue != null) Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => BankSelectionPage(rawData: barcode.rawValue!, riskFlag: false, mockLoc: false)));
      }),
    );
  }
}

class BankSelectionPage extends StatelessWidget {
  final String rawData;
  final bool riskFlag;
  final bool mockLoc;
  const BankSelectionPage({super.key, required this.rawData, required this.riskFlag, required this.mockLoc});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Select Payment Bank")),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          ListTile(
            tileColor: kWhite, leading: const Icon(Icons.account_balance), title: const Text("HDFC Bank"),
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => PinPage(senderBank: "HDFC", receiverData: rawData, riskFlag: riskFlag, mockLoc: mockLoc))),
          ),
          const SizedBox(height: 10),
          ListTile(
            tileColor: kWhite, leading: const Icon(Icons.account_balance), title: const Text("DCB Bank"),
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => PinPage(senderBank: "DCB", receiverData: rawData, riskFlag: riskFlag, mockLoc: mockLoc))),
          ),
        ],
      ),
    );
  }
}

// =========================================================
// 5. PIN & ADAPTIVE VERIFICATION
// =========================================================
class PinPage extends StatefulWidget {
  final String senderBank, receiverData;
  final bool riskFlag, mockLoc;
  const PinPage({super.key, required this.senderBank, required this.receiverData, required this.riskFlag, required this.mockLoc});
  @override
  State<PinPage> createState() => _PinPageState();
}

class _PinPageState extends State<PinPage> {
  final TextEditingController _amount = TextEditingController();
  final TextEditingController _pin = TextEditingController();
  bool _isLoading = false;
  DateTime? _pinStartTime;

  Future<void> _handlePayment() async {
    double amt = double.tryParse(_amount.text) ?? 0;
    if (amt <= 0) return;
    setState(() => _isLoading = true);

    // Capture Behavioral DNA
    int entryTimeMs = _pinStartTime != null ? DateTime.now().difference(_pinStartTime!).inMilliseconds : 500;

    // PREPARE 18-PARAMETER PAYLOAD
    Map<String, dynamic> txPayload = {
      "user_id": JurySession.activeUserPhone,
      "amount": amt,
      "merchant_name": widget.receiverData,
      "is_malicious_link": widget.riskFlag ? 1 : 0,
      "mock_location_enabled": widget.mockLoc ? 1 : 0,
      "pin_entry_time_ms": entryTimeMs,
      "hour_of_day": DateTime.now().hour,
      "is_senior": JurySession.userAge > 60 ? 1 : 0,
      "is_on_call": 0, // In a real app, use telephony package
      "sender_bank": widget.senderBank,
      "is_rooted": 0,
      "is_emulator": 1 // Assuming emulator for demo
    };

    try {
      // 1. CALL ADAPTIVE BACKEND (/verify)
      final verifyRes = await http.post(
        Uri.parse("http://${JurySession.serverIp}:8000/verify"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(txPayload),
      );

      if (verifyRes.statusCode == 200) {
        final res = jsonDecode(verifyRes.body);
        String decision = res['decision']; // ALLOW, WARN, or BLOCK

        // 2. TRIGGER FEEDBACK LOOP (ML Online Learning)
        // FIXED: Added 'tx' key to prevent KeyError in main.py
        await http.post(
          Uri.parse("http://${JurySession.serverIp}:8000/feedback"),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({
            "tx": txPayload, 
            "is_fraud": decision == "BLOCK" ? 1 : 0
          }),
        );

        if (decision == "ALLOW") {
          if (widget.senderBank == "HDFC") JurySession.hdfcBalance -= amt; else JurySession.dcbBalance -= amt;
        }

        if (!mounted) return;
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => ResultPage(status: decision, amount: amt)));
      }
    } catch (e) { 
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Backend Connection Error: $e"))); 
    } finally { setState(() => _isLoading = false); }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Enter UPI PIN")),
      body: Padding(
        padding: const EdgeInsets.all(30),
        child: Column(children: [
          TextField(controller: _amount, keyboardType: TextInputType.number, decoration: const InputDecoration(hintText: "Enter Amount ₹")),
          const SizedBox(height: 20),
          TextField(
            controller: _pin, obscureText: true, maxLength: 4, 
            onChanged: (v) { if (_pinStartTime == null) _pinStartTime = DateTime.now(); },
            decoration: const InputDecoration(hintText: "UPI PIN"),
          ),
          const SizedBox(height: 40),
          if (_isLoading) const CircularProgressIndicator() else ElevatedButton(onPressed: _handlePayment, child: const Text("PROCEED SECURELY")),
        ]),
      ),
    );
  }
}

// =========================================================
// 6. RESULT PAGE
// =========================================================
class ResultPage extends StatelessWidget {
  final String status;
  final double amount;
  const ResultPage({super.key, required this.status, required this.amount});

  @override
  Widget build(BuildContext context) {
    Color bg = status == "ALLOW" ? kSuccess : (status == "WARN" ? Colors.orange : kDanger);
    return Scaffold(
      backgroundColor: bg,
      body: Center(
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(status == "BLOCK" ? Icons.block : Icons.security, size: 100, color: kWhite),
          const SizedBox(height: 20),
          Text("Decision: $status", style: const TextStyle(color: kWhite, fontSize: 32, fontWeight: FontWeight.bold)),
          Text("Amount: ₹$amount", style: const TextStyle(color: kWhite, fontSize: 18)),
          const SizedBox(height: 40),
          ElevatedButton(
            onPressed: () => Navigator.popUntil(context, (r) => r.isFirst), 
            child: const Text("BACK TO HOME", style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ]),
      ),
    );
  }
}