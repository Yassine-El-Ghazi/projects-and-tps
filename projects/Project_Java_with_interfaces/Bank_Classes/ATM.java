package Bank_Classes;

import java.util.ArrayList;

public class ATM {
    protected Service Service;
    protected int ID;
    protected boolean Is_Empty;
    protected ArrayList<Client> Clients=new ArrayList<>();
    protected Client[] Current_Clients=new Client[3];
    protected Bank Bank;
    public ATM(Service service,Bank Bank){
        this.Service = service;
        this.ID = (int)(Math.random()*101);
        this.Bank = Bank;
        Bank.AddATM(this);
        this.Is_Empty = true;
        Bank.AddService(service);
    }
    public boolean Is_Empty() {
        return Is_Empty;
    }
    public int getID() {
        return ID;
    }
    public Bank GetBank(){
        return Bank;
    }
    public int howManyClients_Are_waiting() {
        int counter = 0;
        for (Client currentClient : this.Current_Clients)
            if (currentClient != null)
                counter++;
        return counter;
    }
    public void clientLeave(Client client){
        for(int i=this.place_of_client(client); i<this.Current_Clients.length; i++){
            this.Current_Clients[i-1] = Current_Clients[i];
        }
    }
    public boolean Is_their_a_place_in_quee(){
        return howManyClients_Are_waiting() < 3;
    }
    public String Ask_to_Use_Atm(Client client) {
        String response ;
        if(this.Is_their_a_place_in_quee()){
            response="Welcome to our ATM " +client.getFullName()+" Please have a seat our agent will be with you shortly you are number "+this.place_of_client(client)+".\n";
            this.AddClient(client);
            this.Current_Clients[howManyClients_Are_waiting()] = client;
            this.setIs_Empty(false);
        }
        else{
            response=client.getFullName()+" return later the Atm is Busy";
        }
        return response;
    }
    public int place_of_client(Client client) {
        for(int i=0;i<howManyClients_Are_waiting();i++){
            if(client==Current_Clients[i]){
                return i+1;
            }
        }
        return -1;
    }
    public String Serve_Client() {
        String response ;
        if(this.Is_Empty()){
            response="their is no Client to serve.";
        }
        else{
            response="the Client "+Current_Clients[0].getFullName() +" has been served";
            for(int i=1; i<Current_Clients.length; i++){
                Current_Clients[i-1] = Current_Clients[i];
            }
        }
        return response;
    }
    public void AddClient(Client client){
        this.Clients.add(client);
    }
    public void setIs_Empty(boolean Is_Empty) {
        this.Is_Empty = Is_Empty;
    }
    public String toString(){
        return "Atm [ID=" + ID +" Service: "+Service.getName()+ "]";
    }
}
