public class Test {
    int x;

    Test(String y) {
        x = y;
    }




    public int getX() {
        return x;
    }
}

private class Test1 extends Test{
    String y;

    Test1() {
    }
    y = 4;
}
