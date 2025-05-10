package Bank_Classes;

import java.util.ArrayList;
import java.util.Vector;

public class Bank {
    protected String Name;
    protected String Password_to_Manage;
    protected String Address;
    protected int Id;
    protected ArrayList<ATM> ATMs= new ArrayList<>();
    protected ArrayList<Agence_Service> Agences_Service=new ArrayList<>();
    protected ArrayList<Service> Services=new ArrayList<>();
    public Bank(String name,String address,String password){
        Password_to_Manage=password;
        this.Name = name;
        this.Id=(int)(Math.random() * 101);
        this.Address = address;
    }
    public void AddATM(ATM ATM){
        ATMs.add(ATM);
    }
    public void AddService(Service service){
        Services.add(service);
    }
    public String getName(){
        return Name;
    }
    public int getId(){return Id;}
    public ArrayList<ATM> getATMs(){
        return ATMs;
    }
    public ArrayList<Service> getServices(){
        return Services;
    }
    public ArrayList<Agence_Service> getAgences_Service(){
        return Agences_Service;
    }
    public String getPassword(){
        return Password_to_Manage;
    }
    public String getAddress(){
        return Address;
    }
    public void removeATM(ATM ATM){
        ATMs.remove(ATM);
    }
    public void removeService(Service service){
        Services.remove(service);
    }
    public void removeAgence(Agence_Service agence){
        Agences_Service.remove(agence);
    }
    public void AddAgence_Service(Agence_Service Agence_Service){
        Agences_Service.add(Agence_Service);
    }
    public String toString(){
        return Name+" "+Address+" ";
    }
    public void setPassword(String password){
        Password_to_Manage = password;
    }
    public void setAddress(String address){
        Address = address;
    }
    public void setName(String name){
        Name = name;
    }
    public String to_String(){
        return "Bank[Id="+Id+", Name="+Name+", Addresse="+Address+"]";
    }
}
