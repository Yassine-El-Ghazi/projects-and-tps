package Bank_Classes;

public class Service {
    protected String Name;
    protected int ID;
    public Service(String Name) {
        this.Name = Name;
        this.ID = (int)(Math.random() * 101);
    }
    public String getName() {
        return Name;
    }
    public int getID() {
        return ID;
    }
    public String toString() {
        return "Service [Id="+ID+", Name=" + Name + "]";
    }
}
