import Bank_Classes.*;

import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;

public class Main {
    static  String password="secret";
    static ArrayList<Bank> Banks = new ArrayList<>();
    static ArrayList<Client> Clients = new ArrayList<>();
    static ArrayList<Service> Services=new ArrayList<>();
    static JFrame Main_Frame = new JFrame();
    static JPanel Main_Panel = new JPanel();
    static JLabel L1 = new JLabel("Who are you?");
    static JPanel inputPanel = new JPanel(new GridLayout(4, 2, 10, 10));
    public static void main(String[] args) {
        Main_Frame.setSize(600, 500);
        Main_Frame.setLayout(new BorderLayout());
        Main_Panel.setSize(600, 500);

        Main_Panel.setLayout(new GridLayout(6, 1, 10, 10));
        JButton AppManager = new JButton("App Manager");
        JButton BankManager = new JButton("Bank Manager");
        JButton BankAgent=new JButton("Bank Agent");
        JButton Client=new JButton("Client");
        JButton Exit = new JButton("Exit the application");
        AppManager.addActionListener(e -> AppManagerLogin());
        BankManager.addActionListener(e ->BankManagerLogin() );
        BankAgent.addActionListener(e -> BankAgentLogin());
        Client.addActionListener(e -> clientLogin());
        Exit.addActionListener(e -> System.exit(0));
        Main_Panel.add(L1);
        Main_Panel.add(AppManager);
        Main_Panel.add(BankManager);
        Main_Panel.add(BankAgent);
        Main_Panel.add(Client);
        Main_Panel.add(Exit);
        Main_Frame.add(Main_Panel, BorderLayout.CENTER);
        Main_Frame.setVisible(true);
        refreshPanel();
    }
    private static void AppManagerLogin(){
        inputPanel.removeAll();
        L1.setText("Enter Password: ");
        JPasswordField pass = new JPasswordField();
        pass.setEchoChar('*');
        inputPanel.add(L1);
        inputPanel.add(pass);
        int result=JOptionPane.showConfirmDialog(Main_Frame, inputPanel,"App Manager Login", JOptionPane.OK_CANCEL_OPTION);
        if(result==JOptionPane.OK_OPTION){
            String passText = new String(pass.getPassword());
            if(password.equals(passText)){AppManagerMenu();}
            else {JOptionPane.showMessageDialog(Main_Frame, "Wrong Password");showMainMenu();}
        }
        refreshPanel();}
    private static void BankManagerLogin(){
        if (Banks.size()==0){
            JOptionPane.showMessageDialog(Main_Frame, "There are no banks in the database.");
        }else {
            String m="the banks that exist in the Database are:\n";
            for (Bank b : Banks) {
                m+=b.to_String();
                m+="\n";
            }
            JTextArea message = new JTextArea(m);
            JPasswordField pass = new JPasswordField();
            pass.setEchoChar('*');
            message.setEditable(false);
            inputPanel.removeAll();
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner bank_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(new JLabel());
            inputPanel.add(new JLabel("ID of the Bank you manage:"));
            inputPanel.add(bank_Id);
            inputPanel.add(new JLabel("Password:"));
            inputPanel.add(pass);
            int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                    "Bank Manager", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                String passText = new String(pass.getPassword());
                boolean found=false;
                for (Bank b : Banks) {
                    if ((b.getId() == (int) (bank_Id.getValue())) && (passText.equals(b.getPassword()))) {
                        manageBank(b);
                        found=true;
                    }
                }
                if(!found){
                    JOptionPane.showMessageDialog(Main_Frame, "incorrect credantials");
                    showMainMenu();
                }
            }
            refreshPanel();
        }
    }
    private static void manageBank(Bank b){
        Main_Panel.removeAll();
        inputPanel.removeAll();
        JButton bank_info=new JButton("Change Bank Info");
        JButton manage_Agents=new JButton("Manage Bank Agents");
        JButton manage_Atms=new JButton("Manage Atms");
        JButton return_Back=new JButton("Log out");
        bank_info.addActionListener(e -> bankInfo(b));
        manage_Agents.addActionListener(e -> manageAgents(b));
        manage_Atms.addActionListener(e -> manageAtms(b));
        return_Back.addActionListener(e -> showMainMenu());
        Main_Panel.add(new JLabel("Managing Bank with the Id= "+b.getId()));
        Main_Panel.add(bank_info);
        Main_Panel.add(manage_Agents);
        Main_Panel.add(manage_Atms);
        Main_Panel.add(return_Back);
        refreshPanel();
    }
    private static void bankInfo(Bank b){
        inputPanel.removeAll();
        JTextField bank_name = new JTextField(b.getName());
        JTextField bank_addresse=new JTextField(b.getAddress());
        JPasswordField pass = new JPasswordField();
        inputPanel.add(new JLabel("Name of the Bank:"));
        inputPanel.add(bank_name);
        inputPanel.add(new JLabel("the addresse of the bank:"));
        inputPanel.add(bank_addresse);
        inputPanel.add(new JLabel("the password to manage the bank:"));
        inputPanel.add(pass);
        int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                "Edit Bank info", JOptionPane.OK_CANCEL_OPTION);
        if(result == JOptionPane.OK_OPTION) {
            b.setName(bank_name.getText());
            b.setAddress(bank_addresse.getText());
            b.setPassword(new String(pass.getPassword()));
            JOptionPane.showMessageDialog(Main_Frame, "The bank info were edited successfully.");
            manageBank(b);
        }
        else {manageBank(b);}
        refreshPanel();
    }
    private static void manageAgents(Bank b){
            Main_Panel.removeAll();
            JButton addAgent = new JButton("Add an Agent");
            JButton removeAgent = new JButton("Remove an Agent");
            JButton viewAgents = new JButton("View All Agents");
            JButton affectAgentToAtm = new JButton("Affect an Agent To an Atm");
            JButton returnBack = new JButton("Return Back");
            addAgent.addActionListener(e -> {
                addAgent(b);
            });
            removeAgent.addActionListener(e -> removeAgent(b));
            viewAgents.addActionListener(e -> viewAgents(b));
            returnBack.addActionListener(e -> manageBank(b));
            affectAgentToAtm.addActionListener(e -> affectAgentToAtm(b));
            Main_Panel.add(addAgent);
            Main_Panel.add(removeAgent);
            Main_Panel.add(viewAgents);
            Main_Panel.add(affectAgentToAtm);
            Main_Panel.add(returnBack);
            refreshPanel();
    }
    private static void affectAgentToAtm(Bank b){
        if (b.getAgences_Service().size()==0 || b.getATMs().size()==0){
            JOptionPane.showMessageDialog(Main_Frame, "There are eather no Agents or Atms in the bank.");
        }else {
            String m="the agents that exist in the bank are:\n";
            for (Agence_Service ag : b.getAgences_Service()) {
                m+=ag.toString();
                m+="\n";
            }
            String m2="the Atms that are in the bank are:\n";
            for (ATM atm : b.getATMs()) {
                m2+=atm.toString();
                m2+="\n";
            }
            JTextArea message2=new JTextArea(m2);
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            message2.setEditable(false);
            inputPanel.removeAll();
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner agent_Id = new JSpinner(model);
            JSpinner atm_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(message2);
            inputPanel.add(new JLabel("ID of the Agent you want:"));
            inputPanel.add(agent_Id);
            inputPanel.add(new JLabel("ID of the Atm you want to associete him to:"));
            inputPanel.add(atm_Id);
            int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                    "Associete agent to atm", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                boolean agentFound=false;
                for (Agence_Service ag : b.getAgences_Service()) {
                    if (ag.getID()==(int)(agent_Id.getValue())) {
                        boolean atmfound=false;
                        for (ATM atm : b.getATMs()) {
                            if (atm.getID()==(int)(atm_Id.getValue())) {
                                ag.Affecter_ATM(atm);
                                JOptionPane.showMessageDialog(Main_Frame, "The agent was associeted with the atm successfully.");
                                manageAgents(b);
                            }
                        }
                        if(!atmfound){
                            JOptionPane.showMessageDialog(Main_Frame, "An Atm with that ID was not fond in the bank.");
                            manageAgents(b);
                        }
                    }
                }
                if(!agentFound){
                    JOptionPane.showMessageDialog(Main_Frame, "An agent with that Id was not fond");
                }
            }
            manageAgents(b);
            refreshPanel();
        }
    }
    private static void addAgent(Bank b){
        inputPanel.removeAll();
        JTextField agent_name = new JTextField();
        inputPanel.add(new JLabel("Name of the Agent:"));
        inputPanel.add(agent_name);
        int result=JOptionPane.showConfirmDialog(Main_Frame,inputPanel,"Add an Agent",JOptionPane.OK_CANCEL_OPTION);
        if(result == JOptionPane.OK_OPTION) {
            Agence_Service agt=new Agence_Service(agent_name.getText(),b);
            JOptionPane.showMessageDialog(Main_Frame,"the Agent was added successfully");
        }
        else {manageAgents(b);}
        refreshPanel();
    }
    private static void removeAgent(Bank b){
        if (b.getAgences_Service().isEmpty()){
            JOptionPane.showMessageDialog(Main_Frame, "There are no Agents in the bank.");
        }else {
            String m="the agents that exist in the bank are:\n";
            for (Agence_Service ag : b.getAgences_Service()) {
                m+=ag.toString();
                m+="\n";
            }
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            inputPanel.removeAll();
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner agent_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(new JLabel());
            inputPanel.add(new JLabel("ID of the Agent you want to remove:"));
            inputPanel.add(agent_Id);
            int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                    "Remove an Agent", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                for (Agence_Service ag : b.getAgences_Service()) {
                    if (ag.getID()==(int)(agent_Id.getValue())) {
                        b.getAgences_Service().remove(ag);
                        JOptionPane.showMessageDialog(Main_Frame, "The agent was removed successfully.");
                        manageAgents(b);
                    }
                }
                JOptionPane.showMessageDialog(Main_Frame, "A agent with that Id was not fond");
            }
            manageAgents(b);
            refreshPanel();
        }
    }
    private static void viewAgents(Bank b){
        if (b.getAgences_Service().isEmpty()){
            JOptionPane.showMessageDialog(Main_Frame, "There are no Agents in the bank.");
        }else {
            String result="the agents that exist in the Bank are:\n";
            for (Agence_Service ag : b.getAgences_Service()) {
                result+=ag.toString();
                result+="\n";
            }
            JOptionPane.showMessageDialog(Main_Frame, result);
            manageAgents(b);
        }
    }
    private static void manageAtms(Bank b){
        Main_Panel.removeAll();
        JButton addAtm = new JButton("Add an Atm");
        JButton removeAtm = new JButton("Remove an Atm");
        JButton viewAtms=new JButton("View All Atms");
        JButton returnBack = new JButton("Return Back");
        addAtm.addActionListener(e -> {addAtm(b);});
        removeAtm.addActionListener(e -> removeAtm(b));
        viewAtms.addActionListener(e -> viewAtms(b));
        returnBack.addActionListener(e -> manageBank(b));
        Main_Panel.add(addAtm);
        Main_Panel.add(removeAtm);
        Main_Panel.add(viewAtms);
        Main_Panel.add(returnBack);
        refreshPanel();
    }
    private static void addAtm(Bank b){
        if (Services.isEmpty()){
            JOptionPane.showMessageDialog(Main_Frame, "There are no services for you to add an Atm in the bank.");
        }else {
            inputPanel.removeAll();
            String m="the services that exist  are:\n";
            for(Service s : Services){
                m+=s.toString()+"\n";
            }
            JTextArea Serices_Ids = new JTextArea(m);
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner Service_Id = new JSpinner(model);
            Serices_Ids.setEditable(false);
            inputPanel.add(Serices_Ids);
            inputPanel.add(new JLabel());
            inputPanel.add(new JLabel("ID of the Service you want the Atm to provide:"));
            inputPanel.add(Service_Id);
            int result=JOptionPane.showConfirmDialog(Main_Frame,inputPanel,"Add an Atm",JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                for (Service s : Services) {
                    if (s.getID()==(int)(Service_Id.getValue())) {
                        ATM atm=new ATM(s,b);
                        JOptionPane.showMessageDialog(Main_Frame, "the atm was added successfully.");
                        manageAtms(b);
                    }
                }
                JOptionPane.showMessageDialog(Main_Frame, "A service with that Id was not fond.");
                manageAtms(b);
            }
        }
    }
    private static void removeAtm(Bank b){
        if (b.getATMs().isEmpty()){
            JOptionPane.showMessageDialog(Main_Frame, "There are no Atms in the bank.");
        }else {
            String m="the atms that exist in the bank are:\n";
            for (ATM atm : b.getATMs()) {
                m+=atm.toString();
                m+="\n";
            }
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            inputPanel.removeAll();
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner Atm_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(new JLabel());
            inputPanel.add(new JLabel("ID of the Atm you want to remove:"));
            inputPanel.add(Atm_Id);
            int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                    "Remove an Atm", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                for (ATM atm : b.getATMs()) {
                    if (atm.getID()==(int)(Atm_Id.getValue())) {
                        b.getATMs().remove(atm);
                        JOptionPane.showMessageDialog(Main_Frame, "The atm was removed successfully.");
                        manageAtms(b);
                    }
                }
                JOptionPane.showMessageDialog(Main_Frame, "An atm with that Id was not fond");
            }
            manageAtms(b);
            refreshPanel();
        }
    }
    private static void viewAtms(Bank b){
        if (b.getATMs().isEmpty()){
            JOptionPane.showMessageDialog(Main_Frame, "There are no Atms in the bank.");
        }else {
            String result="the atms that exist in the Bank are:\n";
            for (ATM atm : b.getATMs()) {
                result+=atm.toString();
                result+="\n";
            }
            JOptionPane.showMessageDialog(Main_Frame, result);
            manageAtms(b);
        }
    }
    private static void BankAgentLogin(){
        inputPanel.removeAll();
        String m="the banks that exist in the Database are:\n";
        for (Bank b : Banks) {
            m+=b.to_String();
            m+="\n";
        }
        JTextArea message = new JTextArea(m);
        message.setEditable(false);
        JTextField agentName = new JTextField();
        JPasswordField agentPassword = new JPasswordField();
        agentPassword.setEchoChar('*');
        SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
        JSpinner bank_Id = new JSpinner(model);
        inputPanel.add(message);
        inputPanel.add(new JLabel());
        inputPanel.add(new JLabel("ID of the Bank you are in:"));
        inputPanel.add(bank_Id);
        inputPanel.add(new JLabel("Full Name:"));
        inputPanel.add(agentName);
        inputPanel.add(new JLabel("Password:"));
        inputPanel.add(agentPassword);
        int result=JOptionPane.showConfirmDialog(Main_Frame,inputPanel,"Agent Login",JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            boolean found=false;
            for(Bank b:Banks){
                if(b.getId()==(int)bank_Id.getValue()){
                    String passText = new String(agentPassword.getPassword());
                    for(Agence_Service ag: b.getAgences_Service()){
                        if(ag.getFullName().equals(agentName.getText())){
                            if(ag.getPassword()==passText){
                                agentInterface(ag);
                                found=true;
                            }else if(ag.getPassword()==null){
                                ag.setPassword(passText);
                                agentInterface(ag);
                                found=true;
                            }
                        }
                    }
                }
            }
            if(!found){
                JOptionPane.showMessageDialog(Main_Frame, "Incorrect informations.");
                showMainMenu();
            }
        }
        refreshPanel();
    }
    private static void agentInterface(Agence_Service a){
        Main_Panel.removeAll();
        inputPanel.removeAll();
        JButton editInfo=new JButton("Edit your Info");
        JButton serveClient=new JButton("Serve Client");
        JButton logOut=new JButton("Log out");
        editInfo.addActionListener(e -> agentEditInfo(a));
        serveClient.addActionListener(e -> serveClient(a));
        logOut.addActionListener(e -> showMainMenu());
        Main_Panel.add(editInfo);
        Main_Panel.add(serveClient);
        Main_Panel.add(logOut);
        refreshPanel();
    }
    private static void agentEditInfo(Agence_Service a){
        inputPanel.removeAll();
        JTextArea agentName = new JTextArea(a.getFullName());
        JTextArea agentPassword = new JTextArea();
        inputPanel.add(new JLabel("Full Name:"));
        inputPanel.add(agentName);
        inputPanel.add(new JLabel("Password:"));
        inputPanel.add(agentPassword);
        int result=JOptionPane.showConfirmDialog(Main_Frame,inputPanel,"Agent Edit Info",JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            a.setFullName(agentName.getText());
            a.setPassword(agentPassword.getText());
            JOptionPane.showMessageDialog(Main_Frame, "Agent info Edited successfully.");
        }else{agentInterface(a);}
        refreshPanel();
    }
    private static void serveClient(Agence_Service a){
        if(a.getATM()==null){
            JOptionPane.showMessageDialog(Main_Frame,"You are not affected to any Atm ask your bank manager to affect you one.");
            agentInterface(a);
        }else{
            JOptionPane.showMessageDialog(Main_Frame,a.getATM().Serve_Client());
        }
    }
    private static void clientLogin(){
        inputPanel.removeAll();
        JTextField FullName = new JTextField();
        inputPanel.add(new JLabel("Your Full Name:"));
        inputPanel.add(FullName);
        int result=JOptionPane.showConfirmDialog(Main_Frame,inputPanel,"Client Login",JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            Client client=new Client(FullName.getText());
            Clients.add(client);
            clientInterface(client);
        }else {showMainMenu();}
        refreshPanel();
    }
    private static void clientInterface(Client c){
        Main_Panel.removeAll();
        inputPanel.removeAll();
        JButton goToBank=new JButton("Go to a Bank");
        JButton logOut=new JButton("Log out");
        goToBank.addActionListener(e -> goToBank(c));
        logOut.addActionListener(e -> showMainMenu());
        Main_Panel.add(new JTextField("Client "+c.getFullName()));
        Main_Panel.add(goToBank);
        Main_Panel.add(logOut);
        refreshPanel();
    }
    private static void goToBank(Client c){
        if(Banks.size()==0){
            JOptionPane.showMessageDialog(Main_Frame,"No Bank in the App");
            clientInterface(c);
        }else {
            inputPanel.removeAll();
            String m = "the banks that exist in the App are:\n";
            for (Bank b : Banks) {
                m += b.to_String();
                m += "\n";
            }
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            SpinnerModel model = new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner bank_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(new JLabel());
            inputPanel.add(new JLabel("ID of the Bank you want to use:"));
            inputPanel.add(bank_Id);
            int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel, "Bank To Use", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                boolean found = false;
                for (Bank b : Banks) {
                    if (b.getId() == (int) bank_Id.getValue()) {
                        found = true;
                        useBank(b, c);
                    }
                }
                if (!found) {
                    JOptionPane.showMessageDialog(Main_Frame, "Bank with that Id does not exist in the App");
                    clientInterface(c);
                }
                refreshPanel();
            }
        }
    }
    private static void useBank(Bank b,Client c){
        Main_Panel.removeAll();
        inputPanel.removeAll();
        JButton bankServices=new JButton("Services of the Bank");
        JButton useAtm=new JButton("Use an Atm");
        JButton returnBack=new JButton("Return Back");
        bankServices.addActionListener(e -> bankServices(b,c));
        useAtm.addActionListener(e ->useAtm(b,c));
        returnBack.addActionListener(e ->clientInterface(c));
        Main_Panel.add(new JLabel("Bank: "+b.getName()+" In "+b.getAddress()));
        Main_Panel.add(bankServices);
        Main_Panel.add(useAtm);
        Main_Panel.add(returnBack);
        refreshPanel();
    }
    private static void bankServices(Bank b,Client c){
        if (b.getServices().isEmpty()){
            JOptionPane.showMessageDialog(Main_Frame,"No services in the Bank");
            useBank(b,c);
        }else{
            inputPanel.removeAll();
            String m="the services that this bank provides are:\n";
            for (Service s : b.getServices()) {
                m+=s.getName()+"\n";
            }
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            JOptionPane.showMessageDialog(Main_Frame,message);
        }
    }
    private static void useAtm(Bank b,Client c){
        if(b.getATMs().isEmpty()){
            JOptionPane.showMessageDialog(Main_Frame,"No ATMs in the Bank");
            useBank(b,c);
        }else{
            inputPanel.removeAll();
            String m="the ATMs are in this bank are:\n";
            for (ATM a : b.getATMs()) {
                m+=a.toString()+"\n";
            }
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner atm_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(new JLabel());
            inputPanel.add(new JLabel("ID of the ATM you want to use:"));
            inputPanel.add(atm_Id);
            int result=JOptionPane.showConfirmDialog(Main_Frame,inputPanel,"ATM To Use",JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                boolean found=false;
                for (ATM a : b.getATMs()) {
                    if(a.getID()==(int)atm_Id.getValue()){
                        found=true;
                        if(a.Is_their_a_place_in_quee()){
                            JOptionPane.showMessageDialog(Main_Frame,a.Ask_to_Use_Atm(c));
                            usingAtm(a,c);
                        }else{
                            JOptionPane.showMessageDialog(Main_Frame,a.Ask_to_Use_Atm(c));
                            useBank(b,c);
                        }
                    }
                }
                if(!found){
                    JOptionPane.showMessageDialog(Main_Frame,"ATM with that Id does not exist in the bank");
                    useBank(b,c);
                }
            }
            refreshPanel();
        }
    }
    private static void usingAtm(ATM a,Client c){
        if(a.place_of_client(c)==-1){
            JOptionPane.showMessageDialog(Main_Frame,"thank you for using our ATM");
            useBank(a.GetBank(),c);
        }else{
            Main_Panel.removeAll();
            inputPanel.removeAll();
            JButton place=new JButton("Your Place in the Quee");
            JButton exit=new JButton("Leave the Quee");
            place.addActionListener(e ->JOptionPane.showMessageDialog(Main_Frame,"You are "+a.place_of_client(c)+" in the Quee"));
            exit.addActionListener(e -> useBank(a.GetBank(),c));
            Main_Panel.add(place);
            Main_Panel.add(exit);
        }
        refreshPanel();
    }
    private static void AppManagerMenu(){
        Main_Panel.removeAll();
        JButton manageBanks = new JButton("Manage the Banks");
        JButton manageServices = new JButton("Manage Services");
        JButton returnBack = new JButton("Log out");
        manageBanks.addActionListener(e -> {manageBanks();});
        manageServices.addActionListener(e -> manageServices());
        returnBack.addActionListener(e -> showMainMenu());
        Main_Panel.add(manageBanks);
        Main_Panel.add(manageServices);
        Main_Panel.add(returnBack);
        refreshPanel();
    }
    private static void manageBanks(){
        Main_Panel.removeAll();
        JButton addBank = new JButton("Add a Bank");
        JButton removeBank = new JButton("Remove a Bank");
        JButton viewBanks=new JButton("View Banks");
        JButton returnBack = new JButton("Return Back");
        addBank.addActionListener(e -> {addBank();});
        removeBank.addActionListener(e -> removeBank());
        viewBanks.addActionListener(e -> viewBanks());
        returnBack.addActionListener(e -> AppManagerMenu());
        Main_Panel.add(addBank);
        Main_Panel.add(removeBank);
        Main_Panel.add(viewBanks);
        Main_Panel.add(returnBack);
        refreshPanel();
    }
    private static void addBank(){
        inputPanel.removeAll();
        JTextField bank_name = new JTextField();
        JTextField bank_addresse=new JTextField();
        JPasswordField pass = new JPasswordField();
        inputPanel.add(new JLabel("Name of the Bank:"));
        inputPanel.add(bank_name);
        inputPanel.add(new JLabel("the addresse of the bank:"));
        inputPanel.add(bank_addresse);
        inputPanel.add(new JLabel("the password to manage the bank:"));
        inputPanel.add(pass);
        int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                "Add a bank", JOptionPane.OK_CANCEL_OPTION);
        if(result == JOptionPane.OK_OPTION) {
            Banks.add(new Bank(new String(bank_name.getText()),new String(bank_addresse.getText()),new String(pass.getPassword())));
            JOptionPane.showMessageDialog(Main_Frame, "The bank was added successfully.");
            manageBanks();
        }
        else {manageBanks();}
        refreshPanel();
    }
    private static void removeBank(){
        if (Banks.size()==0){
            JOptionPane.showMessageDialog(Main_Frame, "There are no banks in the database.");
        }else {
            String m="the banks that exist in the Database are:\n";
            for (Bank b : Banks) {
                m+=b.to_String();
                m+="\n";
            }
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            inputPanel.removeAll();
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner bank_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(new JLabel("ID of the Bank you want to remove:"));
            inputPanel.add(bank_Id);
            int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                    "Remove a bank", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                for (Bank b : Banks) {
                    if (b.getId()==(int)(bank_Id.getValue())) {
                        Banks.remove(b);
                        JOptionPane.showMessageDialog(Main_Frame, "The bank was removed successfully.");
                        manageBanks();
                    }
                }
                JOptionPane.showMessageDialog(Main_Frame, "A bank with that Id was not fond");
            }
            manageBanks();
            refreshPanel();
        }
    }
    private static void viewBanks(){
        if (Banks.size()==0){
            JOptionPane.showMessageDialog(Main_Frame, "There are no banks in the database.");
        }else {
            String result="the banks that exist in the Database are:\n";
            for (Bank b : Banks) {
                result+=b.to_String();
                result+="\n";
            }
            JOptionPane.showMessageDialog(Main_Frame, result);
            manageBanks();
        }
    }
    private static void manageServices(){
        Main_Panel.removeAll();
        JButton addService = new JButton("Add a Service");
        JButton removeSevice = new JButton("Remove a service");
        JButton viewServices=new JButton("View Services");
        JButton returnBank = new JButton("Return Back");
        addService.addActionListener(e -> {addService();});
        removeSevice.addActionListener(e -> removeService());
        viewServices.addActionListener(e -> viewServices());
        returnBank.addActionListener(e -> AppManagerMenu());
        Main_Panel.add(addService);
        Main_Panel.add(removeSevice);
        Main_Panel.add(viewServices);
        Main_Panel.add(returnBank);
        refreshPanel();
    }
    static void addService(){
        inputPanel.removeAll();
        JTextField service_name = new JTextField();
        inputPanel.add(new JLabel("What is the Service:"));
        inputPanel.add(service_name);
        int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                "Add a service", JOptionPane.OK_CANCEL_OPTION);
        if(result == JOptionPane.OK_OPTION) {
            Services.add(new Service(service_name.getText()));
            JOptionPane.showMessageDialog(Main_Frame, "The Service was added successfully.");
            manageServices();
        }
        else {manageServices();}
        refreshPanel();
    }
    static void removeService(){
        if (Services.size()==0){
            JOptionPane.showMessageDialog(Main_Frame, "There are no Services in the database.");
        }else {
            inputPanel.removeAll();
            String m="the Services that exist in the Database are:\n";
            for (Service s : Services) {
                m+=s.toString();
                m+="\n";
            }
            JTextArea message = new JTextArea(m);
            message.setEditable(false);
            inputPanel.removeAll();
            SpinnerModel model =new SpinnerNumberModel(0, 0, 100, 1);
            JSpinner service_Id = new JSpinner(model);
            inputPanel.add(message);
            inputPanel.add(new JLabel("ID of the service that you want to remove:"));
            inputPanel.add(service_Id);
            int result = JOptionPane.showConfirmDialog(Main_Frame, inputPanel,
                    "Remove a service", JOptionPane.OK_CANCEL_OPTION);
            if (result == JOptionPane.OK_OPTION) {
                for (Service s : Services) {
                    if (s.getID()==(int)(service_Id.getValue())) {
                        Services.remove(s);
                        JOptionPane.showMessageDialog(Main_Frame, "The service was removed successfully.");
                        manageServices();
                    }
                }
                JOptionPane.showMessageDialog(Main_Frame, "the service was not fond");
                manageServices();
            } else {
                manageServices();
            }
            refreshPanel();
        }
    }
    static void viewServices(){
        if (Services.size()==0){
            JOptionPane.showMessageDialog(Main_Frame, "There are no Services in the App.");
        }else {
            String result="the Services that exist in the App are:\n";
            for (Service s : Services) {
                result+=s.toString();
                result+="\n";
            }
            JOptionPane.showMessageDialog(Main_Frame, result);
            manageServices();
        }
    }
    private static void showMainMenu(){
        Main_Panel.removeAll();
        L1.setText("Who are you?");
        JButton AppManager = new JButton("App Manager");
        JButton BankManager = new JButton("Bank Manager");
        JButton BankAgent=new JButton("Bank Agent");
        JButton Client=new JButton("Client");
        JButton Exit = new JButton("Exit the application");
        AppManager.addActionListener(e -> AppManagerLogin());
        BankManager.addActionListener(e ->BankManagerLogin() );
        BankAgent.addActionListener(e -> BankAgentLogin());
        Client.addActionListener(e -> clientLogin());
        Exit.addActionListener(e -> System.exit(0));
        Main_Panel.add(L1);
        Main_Panel.add(AppManager);
        Main_Panel.add(BankManager);
        Main_Panel.add(BankAgent);
        Main_Panel.add(Client);
        Main_Panel.add(Exit);
        Main_Frame.add(Main_Panel, BorderLayout.CENTER);
        refreshPanel();
    }
    private static void refreshPanel() {
        Main_Panel.revalidate();
        Main_Panel.repaint();
    }
}
