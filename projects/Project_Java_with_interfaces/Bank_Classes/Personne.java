package Bank_Classes;

public abstract class Personne {
    protected String FullName;
    public Personne(String name){
        this.FullName = name;
    }
    public String toString(){
        return FullName;
    }
    public String getFullName(){
        return FullName;
    }
    public void setFullName(String fullName){
        this.FullName = fullName;
    }
}
