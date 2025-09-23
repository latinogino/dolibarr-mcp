#!/usr/bin/env python3
"""Comprehensive test suite for Dolibarr MCP Server."""

import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dolibarr_mcp.config import Config
from src.dolibarr_mcp.dolibarr_client import DolibarrClient, DolibarrAPIError

# Load environment variables
load_dotenv()


class TestColors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{TestColors.HEADER}{TestColors.BOLD}{'=' * 60}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}{text}{TestColors.ENDC}")
    print(f"{TestColors.HEADER}{TestColors.BOLD}{'=' * 60}{TestColors.ENDC}")


def print_test(name, result, details=""):
    """Print test result."""
    if result:
        status = f"{TestColors.OKGREEN}✅ PASS{TestColors.ENDC}"
    else:
        status = f"{TestColors.FAIL}❌ FAIL{TestColors.ENDC}"
    
    print(f"  {status} - {name}")
    if details:
        print(f"       {TestColors.OKCYAN}{details}{TestColors.ENDC}")


async def test_connection(client):
    """Test basic API connection."""
    print_header("🔌 CONNECTION TEST")
    
    try:
        result = await client.get_status()
        print_test("API Connection", True, f"Dolibarr v{result.get('dolibarr_version', 'unknown')}")
        return True
    except Exception as e:
        print_test("API Connection", False, str(e))
        return False


async def test_customers(client):
    """Test customer CRUD operations."""
    print_header("👥 CUSTOMER MANAGEMENT")
    
    test_customer_id = None
    
    try:
        # List customers
        customers = await client.get_customers(limit=5)
        print_test("List Customers", True, f"Found {len(customers)} customers")
        
        # Create customer
        new_customer = await client.create_customer(
            name=f"Test Customer {datetime.now().strftime('%Y%m%d%H%M%S')}",
            email="test@example.com",
            phone="+1234567890",
            address="123 Test Street",
            town="Test City",
            zip="12345"
        )
        test_customer_id = new_customer if isinstance(new_customer, int) else new_customer.get('id')
        print_test("Create Customer", True, f"Created ID: {test_customer_id}")
        
        # Get customer by ID
        if test_customer_id:
            customer = await client.get_customer_by_id(test_customer_id)
            print_test("Get Customer by ID", True, f"Retrieved: {customer.get('name', 'Unknown')}")
            
            # Update customer
            updated = await client.update_customer(
                test_customer_id, 
                email="updated@example.com"
            )
            print_test("Update Customer", True, "Email updated")
            
            # Delete customer
            deleted = await client.delete_customer(test_customer_id)
            print_test("Delete Customer", True, f"Deleted ID: {test_customer_id}")
        
        return True
        
    except Exception as e:
        print_test("Customer Operations", False, str(e))
        # Try to clean up
        if test_customer_id:
            try:
                await client.delete_customer(test_customer_id)
            except:
                pass
        return False


async def test_products(client):
    """Test product CRUD operations."""
    print_header("📦 PRODUCT MANAGEMENT")
    
    test_product_id = None
    
    try:
        # List products
        products = await client.get_products(limit=5)
        print_test("List Products", True, f"Found {len(products)} products")
        
        # Create product
        new_product = await client.create_product(
            label=f"Test Product {datetime.now().strftime('%Y%m%d%H%M%S')}",
            price=99.99,
            description="Test product description",
            stock=100
        )
        test_product_id = new_product if isinstance(new_product, int) else new_product.get('id')
        print_test("Create Product", True, f"Created ID: {test_product_id}")
        
        # Get product by ID
        if test_product_id:
            product = await client.get_product_by_id(test_product_id)
            print_test("Get Product by ID", True, f"Retrieved: {product.get('label', 'Unknown')}")
            
            # Update product
            updated = await client.update_product(
                test_product_id,
                price=149.99
            )
            print_test("Update Product", True, "Price updated")
            
            # Delete product
            deleted = await client.delete_product(test_product_id)
            print_test("Delete Product", True, f"Deleted ID: {test_product_id}")
        
        return True
        
    except Exception as e:
        print_test("Product Operations", False, str(e))
        # Try to clean up
        if test_product_id:
            try:
                await client.delete_product(test_product_id)
            except:
                pass
        return False


async def test_users(client):
    """Test user operations."""
    print_header("👤 USER MANAGEMENT")
    
    try:
        # List users
        users = await client.get_users(limit=5)
        print_test("List Users", True, f"Found {len(users)} users")
        
        if users:
            # Get first user details
            first_user = users[0]
            user_id = first_user.get('id')
            if user_id:
                user = await client.get_user_by_id(user_id)
                print_test("Get User by ID", True, f"Retrieved: {user.get('login', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print_test("User Operations", False, str(e))
        return False


async def test_invoices(client):
    """Test invoice operations."""
    print_header("📄 INVOICE MANAGEMENT")
    
    try:
        # List invoices
        invoices = await client.get_invoices(limit=5)
        print_test("List Invoices", True, f"Found {len(invoices)} invoices")
        
        if invoices:
            # Get first invoice details
            first_invoice = invoices[0]
            invoice_id = first_invoice.get('id')
            if invoice_id:
                invoice = await client.get_invoice_by_id(invoice_id)
                print_test("Get Invoice by ID", True, f"Retrieved Invoice #{invoice.get('ref', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print_test("Invoice Operations", False, str(e))
        return False


async def test_orders(client):
    """Test order operations."""
    print_header("📋 ORDER MANAGEMENT")
    
    try:
        # List orders
        orders = await client.get_orders(limit=5)
        print_test("List Orders", True, f"Found {len(orders)} orders")
        
        if orders:
            # Get first order details
            first_order = orders[0]
            order_id = first_order.get('id')
            if order_id:
                order = await client.get_order_by_id(order_id)
                print_test("Get Order by ID", True, f"Retrieved Order #{order.get('ref', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print_test("Order Operations", False, str(e))
        return False


async def test_contacts(client):
    """Test contact operations."""
    print_header("📇 CONTACT MANAGEMENT")
    
    test_contact_id = None
    
    try:
        # List contacts
        contacts = await client.get_contacts(limit=5)
        print_test("List Contacts", True, f"Found {len(contacts)} contacts")
        
        # Create contact
        new_contact = await client.create_contact(
            firstname="Test",
            lastname=f"Contact {datetime.now().strftime('%Y%m%d%H%M%S')}",
            email="testcontact@example.com"
        )
        test_contact_id = new_contact if isinstance(new_contact, int) else new_contact.get('id')
        print_test("Create Contact", True, f"Created ID: {test_contact_id}")
        
        # Get contact by ID
        if test_contact_id:
            contact = await client.get_contact_by_id(test_contact_id)
            name = f"{contact.get('firstname', '')} {contact.get('lastname', '')}"
            print_test("Get Contact by ID", True, f"Retrieved: {name.strip()}")
            
            # Update contact
            updated = await client.update_contact(
                test_contact_id,
                email="updatedcontact@example.com"
            )
            print_test("Update Contact", True, "Email updated")
            
            # Delete contact
            deleted = await client.delete_contact(test_contact_id)
            print_test("Delete Contact", True, f"Deleted ID: {test_contact_id}")
        
        return True
        
    except Exception as e:
        print_test("Contact Operations", False, str(e))
        # Try to clean up
        if test_contact_id:
            try:
                await client.delete_contact(test_contact_id)
            except:
                pass
        return False


async def test_raw_api(client):
    """Test raw API access."""
    print_header("🔧 RAW API ACCESS")
    
    try:
        # Test raw GET request
        result = await client.dolibarr_raw_api(
            method="GET",
            endpoint="/setup/modules",
            params={"limit": 5}
        )
        print_test("Raw GET Request", True, f"Retrieved {len(result) if isinstance(result, list) else 'data'}")
        
        return True
        
    except Exception as e:
        print_test("Raw API Access", False, str(e))
        return False


async def main():
    """Run all tests."""
    print(f"{TestColors.BOLD}{TestColors.HEADER}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     🚀 DOLIBARR MCP SERVER - COMPREHENSIVE TEST SUITE    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{TestColors.ENDC}")
    
    # Initialize configuration and client
    try:
        config = Config()
        print(f"\n{TestColors.OKGREEN}✅ Configuration loaded successfully{TestColors.ENDC}")
        print(f"   URL: {config.dolibarr_url}")
        print(f"   API Key: {'*' * 20}{config.api_key[-4:]}")
    except Exception as e:
        print(f"\n{TestColors.FAIL}❌ Configuration failed: {e}{TestColors.ENDC}")
        return
    
    # Run tests
    async with DolibarrClient(config) as client:
        results = []
        
        # Run each test suite
        results.append(("Connection", await test_connection(client)))
        results.append(("Users", await test_users(client)))
        results.append(("Customers", await test_customers(client)))
        results.append(("Products", await test_products(client)))
        results.append(("Invoices", await test_invoices(client)))
        results.append(("Orders", await test_orders(client)))
        results.append(("Contacts", await test_contacts(client)))
        results.append(("Raw API", await test_raw_api(client)))
    
    # Print summary
    print_header("📊 TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    failed_tests = total_tests - passed_tests
    
    print(f"\n  Total Tests: {total_tests}")
    print(f"  {TestColors.OKGREEN}Passed: {passed_tests}{TestColors.ENDC}")
    print(f"  {TestColors.FAIL}Failed: {failed_tests}{TestColors.ENDC}")
    
    if failed_tests == 0:
        print(f"\n{TestColors.OKGREEN}{TestColors.BOLD}🎉 ALL TESTS PASSED! 🎉{TestColors.ENDC}")
        print(f"\n{TestColors.OKCYAN}The Dolibarr MCP server is fully operational!{TestColors.ENDC}")
        print(f"{TestColors.OKCYAN}You can now use it with Claude Desktop.{TestColors.ENDC}")
    else:
        print(f"\n{TestColors.WARNING}⚠️ Some tests failed. Check the details above.{TestColors.ENDC}")
        print(f"{TestColors.WARNING}The server may still work for successful operations.{TestColors.ENDC}")
    
    print(f"\n{TestColors.BOLD}Next steps:{TestColors.ENDC}")
    print("1. Ensure Claude Desktop configuration includes this server")
    print("2. Restart Claude Desktop to reload MCP servers")
    print("3. Test by asking Claude to interact with your Dolibarr system")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{TestColors.WARNING}Test suite interrupted by user{TestColors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{TestColors.FAIL}Unexpected error: {e}{TestColors.ENDC}")
        sys.exit(1)
