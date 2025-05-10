package Bank_Classes;

public class Agence_Service extends Personne {
    protected ATM Atm;
    protected int ID;
    protected Bank Bank;
    protected String Password;
    public Agence_Service(String name,Bank Bank) {
        super(name);
        Password=null;
        this.Atm=null;
        this.ID = (int)(Math.random()*101);
        Bank = Bank;
        Bank.AddAgence_Service(this);
    }
    public void  setPassword(String password){
        Password=password;
    }
    public void Affecter_ATM(ATM atm){
        this.Atm = atm;
    }
    public String getPassword(){
        return Password;
    }
    public int getID(){
        return ID;
    }
    public ATM getATM(){
        return Atm;
    }
    public Bank getBank(){
        return Bank;
    }
    public String toString(){
        return "Agent[ID="+ID+", Name="+FullName+"]";
    }
}
