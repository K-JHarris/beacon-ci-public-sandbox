using System;
using Beacon.Poc;
static class Program
{
    static void Expect(int actual, int expected, string label)
    {
        if (actual != expected) throw new Exception(label + ": expected " + expected + ", got " + actual);
        Console.WriteLine("PASS: " + label);
    }

    static void Main()
    {
        Expect(WillMath.Restore(10, 3, 120), 13, "Restores expected amount");
        Expect(WillMath.Restore(119, 10, 120), 120, "Caps at capacity");
        Expect(WillMath.Restore(5, 0, 120), 5, "Zero gain");
        Expect(WillMath.Restore(int.MaxValue - 1, int.MaxValue, int.MaxValue), int.MaxValue, "Overflow-safe addition");
        Expect(WillMath.Restore(0, 0, 0), 0, "Zero capacity");
        try
        {
            WillMath.Restore(5, -1, 120);
            throw new Exception("Expected ArgumentOutOfRangeException for negative gain");
        }
        catch (ArgumentOutOfRangeException)
        {
            Console.WriteLine("PASS: Rejects negative gain");
        }
        Console.WriteLine("PASS: Six license-free CSharp synthetic code checks; not Unity Editor compilation");
    }
}
